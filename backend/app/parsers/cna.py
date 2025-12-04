"""
中央社 (CNA) 解析器

網站: https://www.cna.com.tw
特點: 使用 paragraph 選擇器，過濾 hashtags 和延伸閱讀
"""

from bs4 import BeautifulSoup
from typing import Tuple
from .base import NewsParser


class CNAParser(NewsParser):
    """中央社解析器"""
    
    # CNA 專用停止關鍵字
    STOP_KEYWORDS = ["延伸閱讀", "關鍵字", "點我追蹤", "快加入"]
    
    @staticmethod
    def parse(html: str) -> Tuple[str, str]:
        """解析中央社內容"""
        soup = BeautifulSoup(html, "html.parser")
        
        # 檢查 404
        if soup.find("title", string="404"):
            return "404", "404"
        
        # 標題
        title_elem = soup.find("h1")
        if not title_elem:
            title_elem = soup.find("h1", {"class": "title"})
        title = title_elem.get_text(strip=True) if title_elem else "無標題"
        
        # 內文
        body_elem = soup.find("div", {"class": "paragraph"})
        if not body_elem:
            body_elem = soup.find("div", {"class": "article-body"})
        
        if body_elem:
            for unwanted in body_elem.find_all(["script", "style", "iframe"]):
                unwanted.decompose()
            
            # 移除 "更多文章" (timeline)
            for more_article in body_elem.find_all("div", class_="moreArticle"):
                more_article.decompose()

            # 移除 Google News 推廣
            for gmail_news in body_elem.find_all("div", class_="gmailNews"):
                gmail_news.decompose()
            
            # 取得純文字並按行分割
            lines = body_elem.get_text(separator="\n", strip=True).split("\n")
            cleaned_lines = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # 遇到停止關鍵字則停止
                if any(keyword in line for keyword in CNAParser.STOP_KEYWORDS):
                    break
                    
                # 過濾 hashtag
                if line.startswith("#"):
                    continue
                    
                cleaned_lines.append(line)
            
            body = "\n".join(cleaned_lines)
        else:
            body = "無法取得內文"
        
        return title, body
