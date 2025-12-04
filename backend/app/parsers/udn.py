"""
聯合新聞網 (UDN) 解析器

網站: https://udn.com
特點: 使用 story_art_title 和 story_bady_info 選擇器
"""

import re
from bs4 import BeautifulSoup
from typing import Tuple
from .base import NewsParser


class UDNParser(NewsParser):
    """聯合新聞網解析器"""
    
    # UDN 專用停止標記
    STOP_MARKERS = ['■', '文章來源', '贊助', '延伸閱讀', '推薦閱讀', '相關新聞', '<!--']
    
    @staticmethod
    def parse(html: str) -> Tuple[str, str]:
        """解析聯合新聞網內容"""
        soup = BeautifulSoup(html, "html.parser")
        
        # 檢查 404
        if soup.find("link", {"rel": "canonical", "href": re.compile("e404")}):
            return "404", "404"
        
        # 標題
        title_elem = soup.find("h1", {"id": "story_art_title"})
        if not title_elem:
            title_elem = soup.find("h1", {"class": "article-content__title"})
        title = title_elem.get_text(strip=True) if title_elem else "無標題"
        
        # 內文
        body_elem = soup.find("div", {"id": "story_bady_info"})
        if not body_elem:
            body_elem = soup.find("section", {"class": "article-content__editor"})
        
        if body_elem:
            # 移除廣告等無關內容
            for unwanted in body_elem.find_all(["script", "style", "iframe", "aside"]):
                unwanted.decompose()
            
            # 取得純文字並按行分割
            lines = body_elem.get_text(separator="\n", strip=True).split("\n")
            cleaned_lines = []
            
            for line in lines:
                line = line.strip()
                if not line or len(line) < 10:
                    continue
                
                # 遇到停止標記就結束
                if any(marker in line for marker in UDNParser.STOP_MARKERS):
                    break
                
                # 跳過廣告提示
                if '[廣告]請繼續往下閱讀' in line:
                    continue
                
                # 過濾雜訊符號開頭的短行
                if len(line) < 30 and line[0] in ['►', '▼', '▲', '■', '●', '★', '※']:
                    continue
                
                cleaned_lines.append(line)
            
            body = "\n".join(cleaned_lines)
        else:
            body = "無法取得內文"
        
        return title, body
