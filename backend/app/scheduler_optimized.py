"""
優化的排程器 - 使用新的 Crawler 系統

策略：
- 每個來源獨立排程
- 高頻率（每5-10分鐘）但每次只爬少量新聞
- 避免集中爬取導致的卡頓
"""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from app import database
from app.crawlers import get_crawler
from app.rss_feeds import get_rss_feeds  
from app.sources import get_source_name
from app.crawler import process_news

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def crawl_single_source(source_id: int, rss_urls: list, limit: int = 3):
    """爬取單一來源"""
    source_name = get_source_name(source_id)
    try:
        logger.info(f"🔄 開始爬取: {source_name}")
        
        # 使用新的 crawler 系統
        crawler = get_crawler(source_id, rss_urls)
        if not crawler:
            logger.warning(f"⚠️  {source_name} 沒有可用的爬蟲")
            return
        
        # 獲取新聞列表
        news_items = await crawler.fetch_news_list()
        
        if not news_items:
            logger.info(f"ℹ️  {source_name} 沒有發現新聞")
            return
        
        # 限制處理數量
        news_items = news_items[:limit]
        
        # 處理每則新聞
        async with database.AsyncSessionLocal() as db:
            count = 0
            for item in news_items:
                try:
                    await process_news(db, item.url, source_id)
                    count += 1
                except Exception as e:
                    logger.error(f"處理新聞失敗 {item.url}: {e}")
                    continue
            
            logger.info(f"✅ {source_name} 完成，處理 {count}/{len(news_items)} 則")
    
    except Exception as e:
        logger.error(f"❌ {source_name} 爬取失敗: {e}")

def start_optimized_scheduler():
    """啟動優化的排程器"""
    
    # 獲取所有 RSS feeds (grouped by source_id)
    from app.rss_feeds import RSS_FEEDS
    
    # 為每個來源設定獨立的排程
    initial_delay = 10  # 首次執行延遲（秒）
    
    for i, (source_id, rss_urls) in enumerate(RSS_FEEDS.items()):
        source_name = get_source_name(source_id)
        
        # 根據來源特性設定間隔
        if source_id == 8:  # UDN (使用網頁爬蟲)
            interval_minutes = 10
            limit = 5
        elif source_id == 2:  # 中時 (使用 DrissionPage，較耗資源)
            interval_minutes = 20  # 增加到 20 分鐘
            limit = 2  # 減少到 2 則，降低負載
        else:
            interval_minutes = 10
            limit = 3
        
        # 錯開首次執行時間
        next_run = datetime.now() + timedelta(seconds=initial_delay + i * 30)
        
        scheduler.add_job(
            crawl_single_source,
            trigger=IntervalTrigger(minutes=interval_minutes),
            args=[source_id, rss_urls, limit],
            id=f'crawler_{source_id}',
            name=f'{source_name} 爬蟲',
            replace_existing=True,
            next_run_time=next_run,
            max_instances=1
        )
        
        logger.info(f"📅 已排程: {source_name} (每{interval_minutes}分鐘, 首次: {next_run})")
    
    scheduler.start()
    logger.info(f"🚀 優化排程器已啟動 - {len(RSS_FEEDS)}個來源已分散排程")

def shutdown_optimized_scheduler():
    """關閉排程器"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("⏹️  排程器已關閉")
