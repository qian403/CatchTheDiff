# 爬蟲開發指南

本資料夾包含各新聞來源的爬蟲實作。

## 架構設計

### 職責分離

**Crawler（爬蟲）**：
- 職責：從網站首頁/列表頁或 RSS 獲取新聞 URL 列表
- 輸出：`List[NewsItem(url, title, published_at)]`

**Parser（解析器）**：
- 職責：從單篇新聞 HTML 提取內容並過濾雜訊
- 輸出：`(title, body)`
- 位置：`app/parsers/`

## 檔案結構

```
crawlers/
├── __init__.py       # 模組入口，匯出 get_crawler()
├── base.py           # BaseCrawler 基礎類別
├── rss.py            # RssCrawler (通用 RSS)
├── udn.py            # UdnCrawler
├── chinatimes.py     # ChinatimesCrawler
└── README.md         # 本說明文件
```

## 新增爬蟲

1. 在 `crawlers/` 建立新檔案，例如 `tvbs.py`
2. 繼承 `BaseCrawler` 並實作 `fetch_news_list()` 方法
3. 在 `__init__.py` 的 `CRAWLERS` 字典中註冊

### 範例

```python
# crawlers/tvbs.py
from bs4 import BeautifulSoup
import httpx
from typing import List
from .base import BaseCrawler, NewsItem
from datetime import datetime


class TvbsCrawler(BaseCrawler):
    """TVBS 爬蟲"""
    
    BASE_URL = "https://news.tvbs.com.tw/realtime"
    
    async def fetch_news_list(self) -> List[NewsItem]:
        async with httpx.AsyncClient() as client:
            response = await client.get(self.BASE_URL)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            news_items = []
            for link in soup.find_all('a', href=lambda x: x and '/news/' in x):
                news_items.append(NewsItem(
                    url=link['href'],
                    title=link.get_text(strip=True),
                    published_at=datetime.now()
                ))
            
            return news_items
```

然後在 `__init__.py` 註冊：

```python
from .tvbs import TvbsCrawler

CRAWLERS = {
    # ... 現有的 ...
    9: TvbsCrawler,  # TVBS
}
```

## 注意事項

- 每個爬蟲應該獨立運作，不依賴其他爬蟲
- 處理好錯誤，避免單一來源失效影響整體
- 注意網站的反爬機制，適當設定 headers
- 限制爬取數量（建議 30-50 則），避免過度爬取
