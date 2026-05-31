from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app import models, schemas, crud, database, utils
# 使用優化的排程器 - 分散式高頻爬取以避免卡頓
from app.scheduler_optimized import start_optimized_scheduler, shutdown_optimized_scheduler
# 如需使用原始排程器，改用: from app.scheduler import start_scheduler, shutdown_scheduler
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from cachetools import TTLCache
import hashlib
import json

# Rate limiter configuration
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

# Query cache (30 second TTL, max 100 entries)
query_cache = TTLCache(maxsize=100, ttl=30)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    
    # 啟動優化的分散式排程器
    start_optimized_scheduler()
    
    yield
    
    # Shutdown - 關閉排程器
    shutdown_optimized_scheduler()

app = FastAPI(
    title="CatchTheDiff API",
    description="新聞差異追蹤 API",
    lifespan=lifespan
)

# Add rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware with environment-based configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=database.settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/news", response_model=list[schemas.News])
@limiter.limit("100/minute")
async def read_news(
    request: Request,
    skip: int = 0, 
    limit: int = 30, 
    q: str = None, 
    sources: List[int] = Query(None), 
    date: str = None,
    sort_by: str = "newest"
):
    """
    取得新聞列表
    
    支援分頁、搜尋、多來源篩選、日期篩選與排序
    - sources: 來源 ID 列表 (例如: ?sources=1&sources=2)
    - sort_by: "newest" (最新發布) 或 "recently_changed" (最近變更)
    """
    # Create cache key from query parameters
    cache_key_data = {
        'skip': skip,
        'limit': limit,
        'q': q,
        'sources': sorted(sources) if sources else None,
        'date': date,
        'sort_by': sort_by
    }
    cache_key = hashlib.md5(json.dumps(cache_key_data, sort_keys=True).encode()).hexdigest()
    
    # Check cache
    if cache_key in query_cache:
        return query_cache[cache_key]
    
    # Query database
    async with database.AsyncSessionLocal() as db:
        news_list = await crud.get_news_list(
            db, 
            skip=skip, 
            limit=limit, 
            query=q, 
            sources=sources, 
            date=date,
            sort_by=sort_by
        )
        
        # Cache result
        query_cache[cache_key] = news_list
        return news_list

@app.get("/news/changes", response_model=list[schemas.News])
async def read_changed_news(skip: int = 0, limit: int = 30):
    """
    取得變更紀錄
    
    只回傳有被修改過的新聞（有多個版本），按最後變更時間排序
    """
    async with database.AsyncSessionLocal() as db:
        news_list = await crud.get_changed_news(db, skip=skip, limit=limit)
        return news_list

@app.get("/news/{news_id}", response_model=schemas.News)
async def read_news_item(news_id: int):
    """取得單一新聞詳細資料"""
    async with database.AsyncSessionLocal() as db:
        news = await crud.get_news(db, news_id=news_id)
        if news is None:
            raise HTTPException(status_code=404, detail="News not found")
        return news

# Statistics endpoints
@app.get("/stats")
async def get_stats():
    """Get overview statistics"""
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.sources import get_source_name
    
    async with database.AsyncSessionLocal() as db:
        # Get all news with versions
        all_news_query = select(models.News).options(selectinload(models.News.versions))
        result = await db.execute(all_news_query)
        all_news = result.scalars().all()
        
        total_news = len(all_news)
        
        # Calculate total edits (versions - initial versions)
        total_edits = sum(len(n.versions) - 1 for n in all_news)
        
        # Calculate by source
        source_stats = {}
        for news in all_news:
            source_id = news.source
            if source_id not in source_stats:
                source_stats[source_id] = 0
            source_stats[source_id] += len(news.versions) - 1  # Edits only
        
        # Find most active source
        most_active_source = None
        if source_stats:
            most_active_id = max(source_stats, key=source_stats.get)
            most_active_source = {
                "id": most_active_id,
                "name": get_source_name(most_active_id),
                "editCount": source_stats[most_active_id]
            }
        
        # Find most edited news
        most_edited_news = None
        if all_news:
            most_edited = max(all_news, key=lambda n: len(n.versions))
            if most_edited.versions:
                most_edited_news = {
                    "id": most_edited.id,
                    "title": most_edited.versions[-1].title,
                    "versionCount": len(most_edited.versions)
                }
        
        return {
            "totalNews": total_news,
            "totalEdits": total_edits,
            "mostActiveSource": most_active_source,
            "mostEditedNews": most_edited_news
        }

@app.get("/stats/edit-frequency")
async def get_edit_frequency():
    """Get source edit frequency ranking"""
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.sources import get_source_name
    
    async with database.AsyncSessionLocal() as db:
        # Get all news with versions
        all_news_query = select(models.News).options(selectinload(models.News.versions))
        result = await db.execute(all_news_query)
        all_news = result.scalars().all()
        
        # Calculate by source
        source_stats = {}
        for news in all_news:
            source_id = news.source
            if source_id not in source_stats:
                source_stats[source_id] = {'news': 0, 'edits': 0}
            source_stats[source_id]['news'] += 1
            source_stats[source_id]['edits'] += len(news.versions) - 1  # Edits only
        
        # Convert to ranking list (only sources with edits)
        ranking = []
        for source_id, stats in sorted(source_stats.items(), key=lambda x: x[1]['edits'], reverse=True):
            if stats['edits'] == 0:
                continue
            ranking.append({
                "sourceId": source_id,
                "sourceName": get_source_name(source_id),
                "newsCount": stats['news'],
                "editCount": stats['edits'],
                "editRatio": round(stats['edits'] / stats['news'], 2) if stats['news'] > 0 else 0
            })
        
        return ranking

@app.get("/stats/timeline")
async def get_timeline(days: int = 30):
    """Get daily activity timeline grouped by source"""
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from datetime import datetime
    from app.sources import get_source_name
    import time as time_module
    
    async with database.AsyncSessionLocal() as db:
        # Calculate timestamp range
        now = int(time_module.time())
        start_time = now - (days * 86400)
        
        # Get all news with versions in range
        news_query = (
            select(models.News)
            .options(selectinload(models.News.versions))
            .where(models.News.created_at >= start_time)
        )
        news_result = await db.execute(news_query)
        all_news = news_result.scalars().all()
        
        # Get all versions in range (for edits)
        versions_query = (
            select(models.NewsVersion)
            .where(models.NewsVersion.time >= start_time)
        )
        versions_result = await db.execute(versions_query)
        all_versions = versions_result.scalars().all()
        
        # Create a map of news_id to source
        news_source_map = {n.id: n.source for n in all_news}
        
        # Get all unique sources
        all_sources_query = select(models.News.source).distinct()
        sources_result = await db.execute(all_sources_query)
        all_sources = [s for s in sources_result.scalars().all()]
        
        # Group data by source and date
        source_data = {}
        for source_id in all_sources:
            source_name = get_source_name(source_id)
            daily_data = {}
            
            for i in range(days):
                day_start = start_time + (i * 86400)
                day_end = day_start + 86400
                date_str = datetime.fromtimestamp(day_start).strftime('%Y-%m-%d')
                
                # Count new news for this source on this day
                new_news = sum(1 for n in all_news 
                              if n.source == source_id and day_start <= n.created_at < day_end)
                
                # Count edits (versions that are not the first version)
                edits = 0
                for v in all_versions:
                    if day_start <= v.time < day_end:
                        news_id = v.news_id
                        if news_id in news_source_map and news_source_map[news_id] == source_id:
                            # Check if this is not the initial version
                            news_obj = next((n for n in all_news if n.id == news_id), None)
                            if news_obj and news_obj.versions:
                                # If this version is not the first one, it's an edit
                                if v.id != news_obj.versions[0].id:
                                    edits += 1
                
                daily_data[date_str] = {
                    "newNews": new_news,
                    "edits": edits
                }
            
            source_data[source_id] = {
                "sourceId": source_id,
                "sourceName": source_name,
                "data": daily_data
            }
        
        return {
            "sources": list(source_data.values()),
            "dates": [datetime.fromtimestamp(start_time + (i * 86400)).strftime('%Y-%m-%d') 
                     for i in range(days)]
        }


@app.get("/news/{news_id}/diff", summary="取得新聞版本差異")
async def read_news_diff(news_id: int, v1: int, v2: int, db: AsyncSession = Depends(database.get_db)):
    """取得兩個版本之間的差異"""
    news = await crud.get_news(db, news_id=news_id)
    if news is None:
        raise HTTPException(status_code=404, detail="找不到新聞")
    
    version1 = next((v for v in news.versions if v.time == v1), None)
    version2 = next((v for v in news.versions if v.time == v2), None)
    
    if not version1 or not version2:
        raise HTTPException(status_code=404, detail="找不到指定的版本")
    
    diff_title = utils.compute_diff(version1.title, version2.title)
    diff_body = utils.compute_diff(version1.body, version2.body)
    
    return {"diff_title": diff_title, "diff_body": diff_body}
