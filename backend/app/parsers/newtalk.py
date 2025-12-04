"""
新頭殼 (Newtalk) 新聞解析器

新頭殼的 RSS 包含完整內文，但需要過濾延伸閱讀等雜訊
"""

from bs4 import BeautifulSoup
import re
from .base import NewsParser


class NewtalkParser(NewsParser):
    """新頭殼解析器
    
    特點：
    - 直接從 articleBody div 提取內容
    - 過濾延伸閱讀、現正最夯、廣告等雜訊
    """
    
    @classmethod
    def parse(cls, html: str) -> tuple[str, str]:
        """解析新頭殼新聞內容
        
        Args:
            html: 原始 HTML
            
        Returns:
            (title, body) tuple
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # 提取標題
        title_tag = soup.find('title')
        title = title_tag.string if title_tag else '新頭殼'
        # 移除標題中的 " - 新頭殼" 等後綴
        title = re.sub(r'\s*[-|]\s*(新頭殼|Newtalk).*$', '', title)
        
        # 從 articleBody 提取內容
        article_body = soup.find('div', class_='articleBody')
        if article_body:
            paragraphs = []
            
            # 找所有段落
            for p in article_body.find_all('p'):
                # 跳過廣告和推薦
                if p.get('class'):
                    # 跳過有 class 的段落（通常是廣告或推薦）
                    if 'recommend' in p.get('class'):
                        continue
                
                text = p.get_text(strip=True)
                
                # 過濾雜訊
                if cls._is_noise(text):
                    break  # 遇到延伸閱讀就停止
                
                if text and len(text) > 10:
                    paragraphs.append(text)
            
            if paragraphs:
                body = '\n'.join(paragraphs)
                return title.strip(), body.strip()
        
        # Fallback: 找所有段落
        paragraphs = []
        for p in soup.find_all('p'):
            # 跳過有 class 的段落
            if p.get('class') and 'recommend' in p.get('class'):
                continue
            
            text = p.get_text(strip=True)
            
            if cls._is_noise(text):
                break
            
            if text and len(text) > 10:
                paragraphs.append(text)
        
        if paragraphs:
            body = '\n'.join(paragraphs)
            return title.strip(), body.strip()
        
        # Final fallback 使用 trafilatura
        import trafilatura
        
        body = trafilatura.extract(html, include_comments=False, include_tables=False)
        if not body:
            body = '無法取得內文'
        
        return title.strip(), body.strip()
    
    @classmethod
    def _is_noise(cls, text: str) -> bool:
        """判斷文字是否為雜訊"""
        # 雜訊關鍵字
        noise_keywords = [
            '延伸閱讀',
            'Newtalk提醒您',
            '※Newtalk',
            '更多相關新聞',
            '相關新聞',
            '加入Line',
            '追蹤',
            '現正最夯',
            '熱門新聞',
            '推薦閱讀',
        ]
        
        for keyword in noise_keywords:
            if keyword in text:
                return True
        
        return False
