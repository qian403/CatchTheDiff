"""
中時新聞網 (Chinatimes) 爬蟲

使用 DrissionPage 繞過反爬機制
"""

from DrissionPage import ChromiumPage
from datetime import datetime
from typing import List
import time
from .base import BaseCrawler, NewsItem


class ChinatimesCrawler(BaseCrawler):
    """中時新聞網爬蟲
    
    中時有強反爬機制，使用 DrissionPage 模擬真實瀏覽器
    """
    
    BASE_URL = "https://www.chinatimes.com/realtimenews"
    
    def __init__(self, source_id: int = 2):
        super().__init__(source_id)
    
    async def fetch_news_list(self) -> List[NewsItem]:
        """使用 DrissionPage 爬取中時新聞列表"""
        news_items = []
        
        try:
            # 配置無頭模式（生產環境）
            from DrissionPage import ChromiumOptions
            co = ChromiumOptions()
            co.headless(True)
            co.set_argument('--disable-gpu')
            co.set_argument('--disable-blink-features=AutomationControlled')
            co.set_argument('--no-sandbox')
            co.set_argument('--disable-dev-shm-usage')
            co.set_user_agent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            print("啟動瀏覽器...")
            page = ChromiumPage(co)
            
            try:
                print(f"訪問 {self.BASE_URL}...")
                page.get(self.BASE_URL)
                
                # 優化等待策略
                print("等待頁面加載...")
                page.wait(3)  # 初始等待縮短到 3 秒
                
                # 等待標題元素出現（最多 10 秒）
                found = False
                for i in range(10):
                    try:
                        test_titles = page.eles('tag:h3@class=title')
                        if len(test_titles) > 0:
                            print(f"✓ 頁面已加載")
                            found = True
                            break
                    except:
                        pass
                    page.wait(1)
                
                if not found:
                    print("⚠️  超時，嘗試繼續...")
                
                print(f"頁面標題: {page.title}")
                
                # 尋找標題元素
                print("尋找新聞...")
                title_elements = page.eles('tag:h3@class=title')
                print(f"找到 {len(title_elements)} 個標題")
                
                if len(title_elements) == 0:
                    print("⚠️  未找到新聞，可能頁面未加載完成")
                    return []
                
                for i, h3 in enumerate(title_elements[:40], 1):
                    try:
                        # h3.title 裡面有一個 a 標籤
                        link = h3.ele('tag:a', timeout=0.5)
                        if not link:
                            continue
                        
                        # 取得連結和標題
                        href = link.attr('href')
                        title = link.text.strip()
                        
                        if not href or not title:
                            continue
                        
                        # 只要 realtimenews 的連結
                        if '/realtimenews/' not in href:
                            continue
                        
                        # 構建完整 URL
                        if href.startswith('/'):
                            url = f"https://www.chinatimes.com{href}"
                        else:
                            url = href
                        
                        # 移除 query string
                        url = url.split('?')[0]
                        
                        if len(title) < 5:
                            continue
                        
                        news_items.append(NewsItem(
                            url=url,
                            title=title,
                            published_at=datetime.now()
                        ))
                        
                        if i <= 5:
                            print(f"  ✓ {title[:65]}")
                        
                    except Exception as e:
                        if i <= 3:
                            print(f"  錯誤 {i}: {e}")
                        continue
                
                # 不需要額外等待，直接關閉
                
            finally:
                print("關閉瀏覽器...")
                page.quit()
            
            # 去重
            seen_urls = set()
            unique_items = []
            for item in news_items:
                if item.url not in seen_urls:
                    seen_urls.add(item.url)
                    unique_items.append(item)
            
            print(f"✅ Chinatimes: 找到 {len(unique_items)} 則獨特新聞")
            return unique_items[:30]
        
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return []
