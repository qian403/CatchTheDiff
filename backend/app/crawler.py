import httpx
from bs4 import BeautifulSoup
import time
from sqlalchemy.ext.asyncio import AsyncSession
import googlenewsdecoder
from app import models, crud, schemas
from app.parsers import get_parser
from app.sources import get_source_name

async def fetch_url(url: str):
    """抓取網址內容"""
    # 如果是 Google News 連結，先解碼
    if "news.google.com/rss/articles" in url:
        try:
            pass  # Decoding Google News URL
            from googlenewsdecoder import new_decoderv1
            decoded = new_decoderv1(url)
            if decoded.get("status"):
                url = decoded["decoded_url"]
                pass  # Decoded successfully
            else:
                pass  # Failed to decode
        except Exception as e:
            pass  # Error decoding

    async with httpx.AsyncClient() as client:  # SSL 驗證已啟用

        try:
            response = await client.get(
                url, 
                follow_redirects=True, 
                timeout=10.0,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                }
            )
            response.raise_for_status()
            return response.text
        except Exception as e:
            pass  # Fetch error
            return None

def parse_content(html: str, source_id: int = 0):
    """
    解析 HTML 內容
    
    使用來源專用的解析器，如果沒有則使用智能內容提取
    """
    parser = get_parser(source_id)
    
    try:
        if hasattr(parser, 'parse') and parser != get_parser(0):
            # 使用專用解析器
            title, body = parser.parse(html)
        else:
            # 使用智能內容提取（trafilatura）
            import trafilatura
            from bs4 import BeautifulSoup
            
            # 提取標題
            soup = BeautifulSoup(html, "html.parser")
            title = ""
            
            # 嘗試多種標題選擇器
            if soup.title:
                title = soup.title.string
            elif soup.find('meta', property='og:title'):
                title = soup.find('meta', property='og:title')['content']
            elif soup.find('h1'):
                title = soup.find('h1').get_text(strip=True)
            
            # 清理標題
            if title:
                title = title.strip()
                # 移除常見後綴
                for suffix in [' - 新聞', ' - Rti 中央廣播電臺', ' - 中央廣播電臺']:
                    if title.endswith(suffix):
                        title = title[:-len(suffix)].strip()
            else:
                title = "無標題"
            
            # 使用 trafilatura 提取主要內容
            extracted = trafilatura.extract(
                html,
                include_comments=False,  # 不包含評論
                include_tables=True,     # 包含表格
                no_fallback=False,       # 允許降級提取
                favor_precision=True,    # 偏向精確度而非召回率
                deduplicate=True         # 去重
            )
            
            if extracted:
                body = extracted.strip()
            else:
                # 如果 trafilatura 失敗，使用備用方案
                # 移除 script 和 style 標籤
                for script in soup(["script", "style", "iframe", "nav", "header", "footer"]):
                    script.decompose()
                
                # 嘗試找 article 或 main 標籤
                main_content = soup.find('article') or soup.find('main') or soup.find('div', class_='content')
                
                if main_content:
                    body = main_content.get_text(separator="\n", strip=True)
                else:
                    body = soup.get_text(separator="\n", strip=True)
        
        return title, body
    except Exception as e:
        pass  # Parse error
        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string if soup.title else "解析失敗"
        return title, f"解析失敗: {str(e)}"

import re

def normalize_url(url: str) -> str:
    """
    標準化 URL 以避免重複
    
    目前主要處理：
    1. 自由時報 (LTN): 移除分類路徑，統一格式
       From: https://news.ltn.com.tw/news/society/breakingnews/5266484
       To:   https://news.ltn.com.tw/news/breakingnews/5266484
    """
    try:
        # 自由時報處理
        if "news.ltn.com.tw" in url:
            # Pattern: .../news/[category]/breakingnews/[id] -> .../news/breakingnews/[id]
            match = re.search(r'(https?://news\.ltn\.com\.tw/news)/[^/]+/(breakingnews/\d+)', url)
            if match:
                return f"{match.group(1)}/{match.group(2)}"
                
        return url
    except Exception as e:
        pass  # Normalization error
        return url

async def process_news(db: AsyncSession, url: str, source_id: int):
    """處理單一新聞"""
    # URL 黑名單 - 過濾掉非新聞頁面
    url_blacklist = [
        '/live',           # 直播頁面
        '/realtime',       # 台視即時新聞列表
        '/video',          # 單純影片頁面
        '/playlist',       # 播放列表
        '/channel',        # 頻道頁面
        'ishopping',       # 購物網站
        '/shop',           # 購物頁面
        '/store',          # 商店頁面
        '/product',        # 產品頁面
    ]
    
    # 檢查 URL 是否在黑名單中
    for blacklisted in url_blacklist:
        if blacklisted in url.lower():
            return  # 跳過此 URL
    
    # URL 正規化處理
    normalized_url = normalize_url(url, source_id)
    normalized_id = hashlib.md5(normalized_url.encode()).hexdigest()
    
    # 檢查是否已存在
    news = await crud.get_news_by_normalized_id(db, normalized_id)
    
    # 如果找不到，再嘗試用原始 URL 找 (兼容舊資料)
    if not news:
        news = await crud.get_news_by_url(db, url)
        if news:
            # 如果用舊 URL 找到了，更新其 normalized_id
            news.normalized_id = normalized_id
            await db.commit()
    
    html = await fetch_url(url)
    if not html:
        return  # Cannot fetch content

    title, body = parse_content(html, source_id)
    current_time = int(time.time())
    
    if not news:
        # 建立新新聞
        news_create = schemas.NewsCreate(
            url=url,
            source=source_id,
            normalized_id=normalized_id,
            created_at=current_time,
            last_fetch_at=current_time
        )
        news = await crud.create_news(db, news_create)
        
        # 建立第一個版本
        version = schemas.NewsVersionBase(
            time=current_time,
            title=title,
            body=body
        )
        await crud.create_news_version(db, version, news.id)
        pass  # News created
        
    else:
        # 檢查內容是否有變更
        latest_version = news.versions[-1] if news.versions else None
        
        if not latest_version or latest_version.title != title or latest_version.body != body:
            version = schemas.NewsVersionBase(
                time=current_time,
                title=title,
                body=body
            )
            await crud.create_news_version(db, version, news.id)
            
            # 更新新聞的 last_changed_at
            news.last_changed_at = current_time
            news.last_fetch_at = current_time
            await db.commit()
            pass  # News updated
        else:
            news.last_fetch_at = current_time
            await db.commit()
            pass  # No changes
