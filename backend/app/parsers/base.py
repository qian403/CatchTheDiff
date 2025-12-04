"""
新聞解析器基礎類別

提供所有專用解析器的共用介面和通用解析邏輯
"""

from bs4 import BeautifulSoup
from typing import Tuple


class NewsParser:
    """新聞解析器基礎類別
    
    所有專用解析器都應繼承此類別並實作 parse() 方法
    """
    
    @staticmethod
    def parse_generic(html: str) -> Tuple[str, str]:
        """通用解析器 - 適用於沒有專用解析器的來源"""
        soup = BeautifulSoup(html, "html.parser")
        
        # 取得標題
        title = "無標題"
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
            
        # 如果標題是 Google News，嘗試尋找 h1
        if "Google News" in title or "Google 新聞" in title:
            h1 = soup.find("h1")
            if h1:
                title = h1.get_text(strip=True)
            else:
                og_title = soup.find("meta", property="og:title")
                if og_title and og_title.get("content"):
                    title = og_title.get("content").strip()

        # 移除 script 和 style
        for script in soup(["script", "style", "iframe"]):
            script.decompose()
        
        # 取得內文
        body = soup.get_text(separator="\n", strip=True)
        
        # 基本過濾
        lines = body.split("\n")
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if any(keyword in line for keyword in ["關鍵字", "延伸閱讀", "點我追蹤", "快加入", "相關新聞", "更多新聞"]):
                continue
            if line.startswith("#"):
                continue
            cleaned_lines.append(line)
            
        return title.strip(), "\n".join(cleaned_lines)
    
    @staticmethod
    def parse(html: str) -> Tuple[str, str]:
        """解析 HTML 內容，回傳 (標題, 內文)"""
        return NewsParser.parse_generic(html)
