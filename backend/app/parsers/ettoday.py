"""
ETtoday 解析器

網站: https://www.ettoday.net
特點: 使用 story 選擇器，雜訊較少
"""

from bs4 import BeautifulSoup
from typing import Tuple
from .base import NewsParser


class EttodayParser(NewsParser):
    """ETtoday 解析器"""
    
    @staticmethod
    def parse(html: str) -> Tuple[str, str]:
        """解析 ETtoday 內容"""
        soup = BeautifulSoup(html, "html.parser")
        
        # 檢查 404
        if "404錯誤" in str(soup.title):
            return "404", "404"
        
        # 標題
        title_elem = soup.find("h1", {"class": "title"})
        if not title_elem:
            title_elem = soup.find("h2", {"class": "title"})
        if not title_elem:
            title_elem = soup.find("h1")
        title = title_elem.get_text(strip=True) if title_elem else "無標題"
        
        # 內文
        body_elem = soup.find("div", {"class": "story"})
        if not body_elem:
            body_elem = soup.find("section", {"itemprop": "articleBody"})
        
        if body_elem:
            for unwanted in body_elem.find_all(["script", "style", "iframe"]):
                unwanted.decompose()
            
            # 取得純文字並按行分割
            lines = body_elem.get_text(separator="\n", strip=True).split("\n")
            cleaned_lines = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 過濾廣告行
                if '[廣告]請繼續往下閱讀' in line or '[廣告]' in line:
                    continue
                
                cleaned_lines.append(line)
            
            body = "\n".join(cleaned_lines)
        else:
            body = "無法取得內文"
        
        return title, body
