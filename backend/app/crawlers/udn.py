"""
聯合新聞網 (UDN) 爬蟲

從 UDN 即時新聞頁面爬取新聞列表
"""

import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List
from .base import BaseCrawler, NewsItem


class UdnCrawler(BaseCrawler):
    """聯合新聞網爬蟲"""
    
    # UDN 即時新聞頁面
    BASE_URL = "https://udn.com/news/breaknews"
    
    def __init__(self, source_id: int = 8):
        super().__init__(source_id)
    
    async def fetch_news_list(self) -> List[NewsItem]:
        """從 UDN 即時新聞頁面爬取新聞列表"""
        news_items = []
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        try:
            async with httpx.AsyncClient(verify=False, timeout=15.0, headers=headers) as client:
                response = await client.get(self.BASE_URL)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # UDN 的新聞列表結構
                news_links = soup.find_all('a', href=lambda x: x and '/news/story/' in x)
                
                for link in news_links[:50]:  # 限制最多 50 則
                    url = link.get('href')
                    if not url.startswith('http'):
                        url = f"https://udn.com{url}"
                    
                    # 移除 query string (like ?from=xxx)
                    if '?' in url:
                        url = url.split('?')[0]
                    
                    # 取得標題
                    title = link.get_text(strip=True)
                    if not title or len(title) < 5:
                        continue
                    
                    # UDN 沒有提供發布時間，使用當前時間
                    news_items.append(NewsItem(
                        url=url,
                        title=title,
                        published_at=datetime.now()
                    ))
                
                # 去重（相同 URL 只保留一個）
                seen_urls = set()
                unique_items = []
                for item in news_items:
                    if item.url not in seen_urls:
                        seen_urls.add(item.url)
                        unique_items.append(item)
                
                print(f"UDN Crawler: Found {len(unique_items)} news items")
                return unique_items
        
        except Exception as e:
            print(f"Error fetching UDN news: {e}")
            return []
