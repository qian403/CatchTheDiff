"""
優化的排程器 - 分散式高頻爬取

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
from crawl_rss import crawl_rss_feed
from app.rss_feeds import get_rss_feeds
from app.sources import get_source_name

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def crawl_single_source(source_id: int, feed_url: str, limit: int = 3):
    """爬取單一來源"""
    source_name = get_source_name(source_id)
    try:
        logger.info(f"🔄 開始爬取: {source_name}")
        async with database.AsyncSessionLocal() as db:
            count = await crawl_rss_feed(db, source_id, feed_url, limit=limit)
            logger.info(f"✅ {source_name} 完成，處理 {count} 則")
    except Exception as e:
        logger.error(f"❌ {source_name} 爬取失敗: {e}")

def start_optimized_scheduler():
    """啟動優化的排程器"""
    
    rss_feeds = get_rss_feeds()
    
    # 為每個來源設定獨立的排程
    # 錯開時間以避免集中爬取
    initial_delay = 10  # 首次執行延遲（秒）
    
    for i, (source_id, feed_url) in enumerate(rss_feeds):
        source_name = get_source_name(source_id)
        
        # 根據來源特性設定間隔
        # 中時因為用瀏覽器爬取較慢，間隔更長，每次只爬2則
        if source_id == 2:  # 中時
            interval_minutes = 15
            limit = 2
        else:
            interval_minutes = 10
            limit = 3
        
        # 錯開首次執行時間，避免同時啟動
        next_run = datetime.now() + timedelta(seconds=initial_delay + i * 30)
        
        scheduler.add_job(
            crawl_single_source,
            trigger=IntervalTrigger(minutes=interval_minutes),
            args=[source_id, feed_url, limit],
            id=f'crawler_{source_id}',
            name=f'{source_name} 爬蟲',
            replace_existing=True,
            next_run_time=next_run,
            max_instances=1  # 確保同一來源不會並行爬取
        )
        
        logger.info(f"📅 已排程: {source_name} (每{interval_minutes}分鐘, 首次: {next_run})")
    
    scheduler.start()
    logger.info(f"🚀 優化排程器已啟動 - {len(rss_feeds)}個來源已分散排程")

def shutdown_optimized_scheduler():
    """關閉排程器"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("⏹️  排程器已關閉")
