"""
RSS 爬蟲

包裝現有的 RSS 爬取邏輯
"""

import feedparser
import httpx
from datetime import datetime
from typing import List
from .base import BaseCrawler, NewsItem


class RssCrawler(BaseCrawler):
    """RSS 爬蟲
    
    用於有官方 RSS feed 的新聞來源
    """
    
    def __init__(self, source_id: int, rss_urls: List[str]):
        """
        Args:
            source_id: 新聞來源 ID
            rss_urls: RSS feed URL 列表
        """
        super().__init__(source_id)
        self.rss_urls = rss_urls
    
    async def fetch_news_list(self) -> List[NewsItem]:
        """從 RSS feeds 獲取新聞列表"""
        news_items = []
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for rss_url in self.rss_urls:
                try:
                    response = await client.get(rss_url)
                    feed = feedparser.parse(response.text)
                    
                    for entry in feed.entries:
                        # 解析發布時間
                        published_at = None
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            published_at = datetime(*entry.published_parsed[:6])
                        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                            published_at = datetime(*entry.updated_parsed[:6])
                        else:
                            published_at = datetime.now()
                        
                        # 建立 NewsItem
                        news_items.append(NewsItem(
                            url=entry.link,
                            title=entry.title if hasattr(entry, 'title') else "無標題",
                            published_at=published_at
                        ))
                
                except Exception as e:
                    print(f"Error fetching RSS {rss_url}: {e}")
                    continue
        
        return news_items
