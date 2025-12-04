"""
中央廣播電台 (RTI) 解析器

網站: https://www.rti.org.tw
特點: 使用 trafilatura 提取內容，過濾導航連結和推薦新聞
"""

from bs4 import BeautifulSoup
from typing import Tuple
from .base import NewsParser


class RtiParser(NewsParser):
    """中央廣播電台 (RTI) 解析器"""
    
    # RTI 專用停止標記
    STOP_MARKERS = [
        '回新聞總覽', '回上頁', 'Podcasts URL',
        '相關新聞', '延伸閱讀', '更多新聞', '熱門新聞',
    ]
    
    # RTI 專用雜訊模式
    NOISE_PATTERNS = ['訂閱複製', '分享', '追蹤', '下載']
    
    # 標題後綴清理
    TITLE_SUFFIXES = [
        '-新聞-Rti 中央廣播電臺',  # 最長的先匹配
        ' - Rti 中央廣播電臺',
        ' - 中央廣播電臺',
        ' - 新聞',
    ]
    
    @staticmethod
    def parse(html: str) -> Tuple[str, str]:
        """解析 RTI 內容"""
        soup = BeautifulSoup(html, "html.parser")
        
        # 標題
        title_elem = soup.find("h2")
        if not title_elem:
            title_elem = soup.find("h1")
        if not title_elem:
            og_title = soup.find("meta", property="og:title")
            if og_title:
                title = og_title.get("content", "無標題")
            else:
                title = "無標題"
        else:
            title = title_elem.get_text(strip=True)
        
        # 清理標題後綴
        for suffix in RtiParser.TITLE_SUFFIXES:
            if title.endswith(suffix):
                title = title[:-len(suffix)].strip()
        
        # 內文 - 使用 trafilatura 提取
        import trafilatura
        extracted = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=True,
            no_fallback=False,
            favor_precision=True,
            deduplicate=True
        )
        
        if extracted:
            lines = extracted.split('\n')
            cleaned_lines = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 遇到停止標記就結束
                if any(marker in line for marker in RtiParser.STOP_MARKERS):
                    break
                
                # 過濾雜訊行
                if any(pattern in line for pattern in RtiParser.NOISE_PATTERNS) and len(line) < 50:
                    continue
                
                # 過濾推薦新聞標題（以數字結尾）
                if len(line) < 80 and len(line) > 10 and line[-1:].isdigit() and not line[-2:-1].isdigit():
                    continue
                
                # 過濾時間戳行
                if len(line) < 20 and any(ts in line for ts in ['小時', '分鐘', '天前', '天']):
                    continue
                
                cleaned_lines.append(line)
            
            body = '\n'.join(cleaned_lines)
        else:
            body = "無法取得內文"
        
        return title, body
