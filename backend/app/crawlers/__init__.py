"""
爬蟲模組

提供統一的新聞爬取介面，支援 RSS 和網頁爬蟲
"""

from typing import Type, Dict
from .base import BaseCrawler, NewsItem
from .rss import RssCrawler
from .udn import UdnCrawler
from .chinatimes import ChinatimesCrawler


# 爬蟲映射表
# key: source_id, value: Crawler class
CRAWLERS: Dict[int, Type[BaseCrawler]] = {
    8: UdnCrawler,        # 聯合新聞網
    2: ChinatimesCrawler,  # 中時新聞網
}


def get_crawler(source_id: int, rss_urls: list = None) -> BaseCrawler:
    """取得對應來源的爬蟲
    
    Args:
        source_id: 新聞來源 ID
        rss_urls: RSS feed URLs (如果使用 RSS 爬蟲)
        
    Returns:
        對應的爬蟲實例
    """
    # 如果有專用的網頁爬蟲，優先使用
    if source_id in CRAWLERS:
        return CRAWLERS[source_id](source_id)
    
    # 否則使用 RSS 爬蟲（如果有提供 RSS URLs）
    if rss_urls:
        return RssCrawler(source_id, rss_urls)
    
    # 都沒有就返回 None
    return None


# 匯出公開 API
__all__ = [
    'get_crawler',
    'CRAWLERS',
    'BaseCrawler',
    'NewsItem',
    'RssCrawler',
    'UdnCrawler',
    'ChinatimesCrawler',
]
