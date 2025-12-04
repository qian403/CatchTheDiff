from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from app import models, schemas

async def get_news_list(db: AsyncSession, skip: int = 0, limit: int = 30, query: str = None, sources: list[int] = None, date: str = None, sort_by: str = "newest"):
    """取得新聞列表"""
    
    stmt = select(models.News).options(selectinload(models.News.versions))
    
    if query:
        # Search in the title of the latest version
        # Join with NewsVersion to search in title
        from sqlalchemy import exists, and_
        
        subquery = (
            select(models.NewsVersion.news_id)
            .where(models.NewsVersion.title.contains(query))
            .distinct()
        )
        
        stmt = stmt.where(models.News.id.in_(subquery))
    
    if sources:
        stmt = stmt.where(models.News.source.in_(sources))
        
    if date:
        try:
            from datetime import datetime, timedelta
            import pytz
            
            # Parse date string (YYYY-MM-DD)
            target_date = datetime.strptime(date, "%Y-%m-%d")
            
            # Convert to Taiwan time range
            tw_tz = pytz.timezone('Asia/Taipei')
            start_dt = tw_tz.localize(target_date)
            end_dt = start_dt + timedelta(days=1)
            
            start_ts = int(start_dt.timestamp())
            end_ts = int(end_dt.timestamp())
            
            stmt = stmt.where(models.News.created_at >= start_ts, models.News.created_at < end_ts)
        except ValueError:
            pass  # Ignore invalid date format
    
    if sort_by == "recently_changed":
        stmt = stmt.order_by(models.News.last_changed_at.desc())
    else:
        # Default to newest
        stmt = stmt.order_by(models.News.created_at.desc())
        
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_changed_news(db: AsyncSession, skip: int = 0, limit: int = 30):
    """取得有變更過的新聞 (有多個版本的新聞)"""
    
    # 子查詢：統計每則新聞的版本數
    version_count = (
        select(
            models.NewsVersion.news_id,
            func.count(models.NewsVersion.id).label('version_count')
        )
        .group_by(models.NewsVersion.news_id)
        .having(func.count(models.NewsVersion.id) > 1)
        .subquery()
    )
    
    # 主查詢：取得有多個版本的新聞，按最後變更時間排序
    stmt = (
        select(models.News)
        .options(selectinload(models.News.versions))
        .join(version_count, models.News.id == version_count.c.news_id)
        .order_by(models.News.last_changed_at.desc())
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_news(db: AsyncSession, news_id: int):
    """取得單一新聞詳細資料"""
    result = await db.execute(
        select(models.News)
        .options(selectinload(models.News.versions))
        .where(models.News.id == news_id)
    )
    return result.scalars().first()

async def get_news_by_url(db: AsyncSession, url: str):
    """透過 URL 取得新聞"""
    result = await db.execute(
        select(models.News)
        .options(selectinload(models.News.versions))
        .where(models.News.url == url)
    )
    return result.scalars().first()

async def get_news_by_normalized_id(db: AsyncSession, normalized_id: str):
    """透過 Normalized ID 取得新聞"""
    result = await db.execute(
        select(models.News)
        .options(selectinload(models.News.versions))
        .where(models.News.normalized_id == normalized_id)
    )
    return result.scalars().first()

async def create_news(db: AsyncSession, news: schemas.NewsCreate):
    """建立新聞"""
    db_news = models.News(**news.dict())
    db.add(db_news)
    await db.commit()
    await db.refresh(db_news)
    return db_news

async def create_news_version(db: AsyncSession, version: schemas.NewsVersionBase, news_id: int):
    """建立新聞版本"""
    db_version = models.NewsVersion(**version.dict(), news_id=news_id)
    db.add(db_version)
    await db.commit()
    await db.refresh(db_version)
    return db_version
