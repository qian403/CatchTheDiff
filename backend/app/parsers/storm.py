"""
風傳媒 (Storm) 新聞解析器

直接從 HTML DOM 結構提取內容
"""

from bs4 import BeautifulSoup
import re
from .base import NewsParser


class StormParser(NewsParser):
    """風傳媒解析器
    
    特點：
    - 直接從 DOM 提取 data-test-block="TEXT" 的內容
    - 自動過濾廣告、相關文章等雜訊
    """
    
    @classmethod
    def parse(cls, html: str) -> tuple[str, str]:
        """解析風傳媒新聞內容
        
        Args:
            html: 原始 HTML
            
        Returns:
            (title, body) tuple
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # 提取標題
        title_tag = soup.find('title')
        title = title_tag.string if title_tag else '風傳媒'
        # 移除標題中的 " - 風傳媒" 後綴
        title = re.sub(r'\s*[-|]\s*風傳媒.*$', '', title)
        
        # 方法1：從 DOM 結構提取內容
        article = soup.find('article', id='editorWrapper')
        if article:
            paragraphs = []
            
            # 找所有 data-test-block="TEXT" 的區塊
            text_blocks = article.find_all('div', {'data-test-block': 'TEXT'})
            
            for block in text_blocks:
                # 提取所有段落文字
                paragraphs_in_block = block.find_all('p')
                for p in paragraphs_in_block:
                    # 移除所有 a 標籤但保留文字
                    # 檢查是否是相關文章連結
                    if '相關報導' in p.get_text() or '更多文章' in p.get_text():
                        continue
                    
                    # 檢查是否是宣傳區塊（通常在 blockquote 或含特定文字）
                    if p.find_parent('blockquote'):
                        continue
                    
                    # 提取純文字
                    text = p.get_text(strip=True)
                    
                    # 過濾雜訊
                    if cls._is_noise(text):
                        continue
                    
                    if text:
                        paragraphs.append(text)
            
            if paragraphs:
                body = '\n'.join(paragraphs)
                return title.strip(), body.strip()
        
        # 方法2：Fallback 使用 trafilatura
        import trafilatura
        
        body = trafilatura.extract(html, include_comments=False, include_tables=False)
        if not body:
            body = '無法取得內文'
        
        return title.strip(), body.strip()
    
    @classmethod
    def _is_noise(cls, text: str) -> bool:
        """判斷文字是否為雜訊"""
        if not text or len(text) < 10:
            return True
        
        # 雜訊關鍵字
        noise_keywords = [
            '訂閱',
            '加入風傳媒',
            '風傳媒VIP',
            '零廣告',
            '加入Line',
            '掌握最新',
            '完整內容點我',
            '更多新聞請搜尋',
        ]
        
        for keyword in noise_keywords:
            if keyword in text:
                return True
        
        return False
