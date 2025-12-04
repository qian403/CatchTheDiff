"""
TVBS 新聞解析器

從 article_content div 提取內容並過濾廣告和宣傳
"""

from bs4 import BeautifulSoup
import re
from .base import NewsParser


class TvbsParser(NewsParser):
    """TVBS 解析器
    
    特點：
    - 從 div.article_content 提取內容
    - 過濾業務宣傳、廣告、Google News 連結等雜訊
    """
    
    @classmethod
    def parse(cls, html: str) -> tuple[str, str]:
        """解析 TVBS 新聞內容
        
        Args:
            html: 原始 HTML
            
        Returns:
            (title, body) tuple
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # 提取標題
        title_tag = soup.find('h1', class_='title')
        if not title_tag:
            title_tag = soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else 'TVBS'
        # 移除標題中的 " - TVBS" 等後綴
        title = re.sub(r'\s*[-|]\s*TVBS.*$', '', title)
        
        # 從 article_content 提取內容
        article_content = soup.find('div', class_='article_content')
        if article_content:
            # 先移除廣告和宣傳區塊
            for unwanted_class in ['guangxuan', 'widely_declared', 'ad_pc', 'ad_mo', 'embed']:
                for unwanted in article_content.find_all('div', class_=unwanted_class):
                    unwanted.decompose()
            
            # 移除廣告區塊（align="center" 通常是廣告）
            for div in article_content.find_all('div', align='center'):
                div.decompose()
            
            # 移除 iframe 和 script
            for tag in article_content.find_all(['iframe', 'script']):
                tag.decompose()
            
            # 移除文末標記
            for marker in article_content.find_all('div', id='article-end-marker'):
                marker.decompose()
            
            # 提取純文字
            text = article_content.get_text(separator='\n', strip=True)
            
            # 清理文字
            lines = []
            for line in text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                # 過濾雜訊
                if cls._is_noise(line):
                    continue
                
                lines.append(line)
            
            if lines:
                body = '\n'.join(lines)
                return title.strip(), body.strip()
        
        # Fallback 使用 trafilatura
        import trafilatura
        
        body = trafilatura.extract(html, include_comments=False, include_tables=False)
        if not body:
            body = '無法取得內文'
        
        return title.strip(), body.strip()
    
    @classmethod
    def _is_noise(cls, text: str) -> bool:
        """判斷文字是否為雜訊"""
        if not text or len(text) < 5:
            return True
        
        # 雜訊關鍵字
        noise_keywords = [
            '加入TVBS',
            'TVBS粉絲',
            '登錄抽',
            '數位紅包',
            '行車出遊陷阱多',
            '修車強制險',
            '班機取消',
            '延伸閱讀',
            '相關新聞',
            '你可能會喜歡',
            '人氣點閱榜',
            'Google News',
            '資料來源：',
            '在 Threads 查看',
            '在 Instagram 查看',
            '在 Facebook 查看',
            '在 Twitter 查看',
        ]
        
        for keyword in noise_keywords:
            if keyword in text:
                return True
        
        # 過濾掉只有 emoji 或符號的行
        if text.startswith('👉') or text.startswith('◤'):
            return True
        
        return False
