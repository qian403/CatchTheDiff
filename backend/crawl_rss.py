"""
RSS 爬蟲

從 RSS Feeds 自動發現並抓取新聞
"""

import asyncio
import feedparser
from sqlalchemy.ext.asyncio import AsyncSession
from app import database, crawler
from app.rss_feeds import get_rss_feeds
from app.sources import get_source_name

async def crawl_rss_feed(db: AsyncSession, source_id: int, feed_url: str, limit: int = 10):
    """
    爬取單一 RSS Feed
    
    Args:
        db: 資料庫 session
        source_id: 新聞來源 ID
        feed_url: RSS Feed 網址
        limit: 最多處理幾則新聞 (預設 10)
    """
    source_name = get_source_name(source_id)
    pass  # Crawling RSS feed
    
    try:
        # 解析 RSS
        feed = feedparser.parse(feed_url)
        
        if not feed.entries:
            return 0  # No entries found
        
        pass  # Found entries
        
        # 處理每則新聞
        processed = 0
        for entry in feed.entries[:limit]:
            if hasattr(entry, 'link'):
                url = entry.link
                
                # 跳過 Google News 的重定向鏈接
                if 'news.google.com' in url:
                    continue  # Skip Google News redirect
                
                pass  # Processing entry
                try:
                    # 檢查新聞是否已存在且超過 7 天
                    from app import crud
                    import time as time_module
                    
                    existing_news = await crud.get_news_by_url(db, url)
                    current_time = int(time_module.time())
                    
                    if existing_news:
                        # 計算新聞年齡（秒）
                        news_age = current_time - existing_news.created_at
                        # 7 天 = 604800 秒
                        if news_age > 604800:
                            continue  # News too old
                            continue
                    
                    await crawler.process_news(db, url, source_id)
                    processed += 1
                except Exception:
                    pass  # Processing failed
        
        return processed  # Completed
        
    except Exception as e:
        return 0  # Parse failed

async def crawl_all_rss(source_id: int = None, limit_per_feed: int = 10):
    """
    爬取所有 RSS Feeds 和自定義爬蟲
    
    Args:
        source_id: 指定來源 ID，None 表示爬取所有來源
        limit_per_feed: 每個 feed 最多處理幾則新聞
    """
    total_processed = 0
    
    # 特殊處理：中時新聞網使用自定義爬蟲
    should_crawl_chinatimes = source_id is None or source_id == 2
    
    if should_crawl_chinatimes:
        pass  # Crawling chinatimes
        
        try:
            from app.chinatimes_crawler import ChinatimesCrawler
            crawler_obj = ChinatimesCrawler(headless=True)
            
            try:
                # 獲取新聞列表
                urls = crawler_obj.get_news_list(limit=limit_per_feed)
                
                # 處理每則新聞
                async with database.AsyncSessionLocal() as db:
                    for url in urls:
                        try:
                            # 使用中時專用爬蟲提取內容
                            article = crawler_obj.extract_article(url)
                            
                            if not article:
                                continue  # Cannot extract
                                continue
                            
                            # 手動創建新聞記錄
                            from app import crud, schemas
                            from datetime import datetime
                            import time as time_module
                            
                            # 檢查新聞是否已存在
                            existing_news = await crud.get_news_by_url(db, url)
                            current_time = int(time_module.time())
                            
                            # 如果新聞已存在且超過 7 天，跳過
                            if existing_news:
                                news_age = current_time - existing_news.created_at
                                if news_age > 604800:  # 7 天 = 604800 秒
                                    print(f"  ⏭️  跳過：新聞已超過 7 天 (ID: {existing_news.id})")
                                    continue
                            
                            
                            if existing_news:
                                latest_version = existing_news.versions[-1] if existing_news.versions else None
                                
                                if latest_version and (
                                    latest_version.title != article['title'] or 
                                    latest_version.body != article['body']
                                ):
                                    # 創建新版本
                                    version_data = schemas.NewsVersionBase(
                                        time=current_time,
                                        title=article['title'],
                                        body=article['body']
                                    )
                                    await crud.create_news_version(db, version_data, existing_news.id)
                                    
                                    # 更新 last_changed_at
                                    existing_news.last_changed_at = current_time
                                    existing_news.last_fetch_at = current_time
                                    await db.commit()
                                    total_processed += 1
                                else:
                                    # 只更新 last_fetch_at
                                    existing_news.last_fetch_at = current_time
                                    await db.commit()
                            else:
                                # 創建新新聞
                                news_data = schemas.NewsCreate(
                                    url=url,
                                    normalized_id=url,
                                    source=2,
                                    created_at=current_time,
                                    last_fetch_at=current_time,
                                    last_changed_at=0,
                                    error_count=0
                                )
                                new_news = await crud.create_news(db, news_data)
                                
                                # 創建第一個版本
                                version_data = schemas.NewsVersionBase(
                                    time=current_time,
                                    title=article['title'],
                                    body=article['body']
                                )
                                await crud.create_news_version(db, version_data, new_news.id)
                                total_processed += 1
                                
                        except Exception:
                            pass  # Processing failed
            finally:
                crawler_obj.close()
                
            pass  # Chinatimes crawl completed
            
        except Exception:
            pass  # Chinatimes crawler error
    
    # 處理其他 RSS feeds
    feeds = get_rss_feeds(source_id)
    
    # 排除中時新聞網 (source_id=2)
    feeds = [(sid, feed_url) for sid, feed_url in feeds if sid != 2]
    
    if not feeds:
        return total_processed if should_crawl_chinatimes else 0  # No RSS feeds
    
    print(f"\n{'='*60}")
    print(f"🚀 開始 RSS 爬蟲任務")
    print(f"📊 共 {len(feeds)} 個 RSS Feeds")
    print(f"{'='*60}")
    
    async with database.AsyncSessionLocal() as db:
        for sid, feed_url in feeds:
            processed = await crawl_rss_feed(db, sid, feed_url, limit_per_feed)
            total_processed += processed
    
    return total_processed  # All done

async def main():
    """執行 RSS 爬蟲"""
    import sys
    
    if len(sys.argv) > 1:
        source_id = int(sys.argv[1])
        await crawl_all_rss(source_id=source_id, limit_per_feed=5)
    else:
        # 預設爬取所有來源，每個 feed 只取 3 則
        await crawl_all_rss(limit_per_feed=3)

if __name__ == "__main__":
    asyncio.run(main())
