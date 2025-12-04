"""
自由時報 (LTN) 解析器

網站: https://news.ltn.com.tw
特點: 使用重複檢測避免推薦新聞，過濾推廣內容
"""

from bs4 import BeautifulSoup
from typing import Tuple
from .base import NewsParser


class LibertytimesParser(NewsParser):
    """自由時報解析器"""
    
    # LTN 專用推廣關鍵字
    PROMO_KEYWORDS = [
        '不用抽', '不用搶', '現在用APP', '馬上領', '優惠券',
        '收藏', '追蹤', '訂閱', '加入', '分享',
        '相關新聞', '延伸閱讀', '更多新聞', '推薦', '熱門'
    ]
    
    @staticmethod
    def parse(html: str) -> Tuple[str, str]:
        """解析自由時報內容"""
        soup = BeautifulSoup(html, "html.parser")
        
        # 標題
        title_elem = soup.find("h1")
        if not title_elem:
            title_elem = soup.find("h1", {"data-desc": "文章標題"})
        if not title_elem:
            og_title = soup.find("meta", property="og:title")
            if og_title:
                title = og_title.get("content", "無標題")
            else:
                title = "無標題"
        else:
            title = title_elem.get_text(strip=True)
        
        # 內文
        body_elem = soup.find("div", {"class": "content"})
        if not body_elem:
            body_elem = soup.find("div", {"class": "text"})
        if not body_elem:
            body_elem = soup.find("div", {"itemprop": "articleBody"})
        
        if body_elem:
            # 移除無關元素
            for unwanted in body_elem.find_all(["script", "style", "iframe", "nav", "aside"]):
                unwanted.decompose()
            
            # 移除 "上一則/下一則" 區塊
            for see_more in body_elem.find_all("div", class_=lambda x: x and "see_more" in x):
                see_more.decompose()
            
            # 提取所有段落
            paragraphs = body_elem.find_all("p")
            body_parts = []
            seen_content = set()  # 用於檢測重複內容
            
            for p in paragraphs:
                text = p.get_text(strip=True)
                
                # 過濾太短的段落
                if len(text) < 20:
                    continue
                
                # 檢查重複（使用前100字作為去重鍵）
                text_key = text[:100]
                if text_key in seen_content:
                    break  # 重複內容開始，停止提取
                seen_content.add(text_key)
                
                # 過濾看起來像標題的內容
                if len(text) < 60 and ('！' in text or '？' in text) and '。' not in text:
                    break
                
                # 過濾推廣內容
                if any(keyword in text for keyword in LibertytimesParser.PROMO_KEYWORDS):
                    continue
                
                body_parts.append(text)
            
            body = "\n\n".join(body_parts) if body_parts else "無法取得內文"
        else:
            body = "無法取得內文"
        
        return title, body
