"""
自動排程爬蟲

使用 APScheduler 定時執行 RSS 爬蟲任務
"""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from app import database
from crawl_rss import crawl_all_rss

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 建立排程器
scheduler = AsyncIOScheduler()

async def scheduled_crawl_task():
    """定時爬蟲任務"""
    try:
        logger.info(f"🕒 開始執行定時爬蟲任務 - {datetime.now()}")
        
        await crawl_all_rss(limit_per_feed=5)
        
        logger.info(f"✅ 定時爬蟲任務完成 - {datetime.now()}")
    except Exception as e:
        logger.error(f"❌ 定時爬蟲任務失敗: {e}")

def start_scheduler():
    """啟動排程器"""
    from datetime import datetime, timedelta
    
    # 每 30 分鐘執行一次爬蟲，立即執行第一次
    next_run = datetime.now() + timedelta(seconds=10)  # 10秒後執行第一次
    
    scheduler.add_job(
        scheduled_crawl_task,
        trigger=IntervalTrigger(minutes=30),
        id='rss_crawler',
        name='RSS 新聞爬蟲',
        replace_existing=True,
        next_run_time=next_run  # 設定下次執行時間
    )
    
    scheduler.start()
    logger.info(f"📅 排程器已啟動 - RSS 爬蟲將每 30 分鐘執行一次，首次執行: {next_run}")

def shutdown_scheduler():
    """關閉排程器"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("📅 排程器已關閉")
