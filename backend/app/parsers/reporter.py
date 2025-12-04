"""
報導者 (Reporter/twreporter) 解析器

網站: https://www.twreporter.org
特點: 使用 trafilatura 提取，過濾文末的延伸閱讀推薦文章
"""

from typing import Tuple
from .base import NewsParser


class ReporterParser(NewsParser):
    """報導者解析器"""
    
    # Reporter 專用停止標記
    STOP_MARKERS = [
        '延伸閱讀', '相關文章', '推薦閱讀', '更多報導',
        '訂閱', '會員', '贊助', '捐款'
    ]
    
    @staticmethod
    def parse(html: str) -> Tuple[str, str]:
        """解析報導者內容"""
        import trafilatura
        
        # 使用 trafilatura 提取內容
        extracted = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=True,
            no_fallback=False,
            favor_precision=True,
            deduplicate=True
        )
        
        if not extracted:
            return "無法取得內文", "無法取得內文"
        
        # 從提取的內容中獲取標題和內文
        lines = extracted.split('\n')
        
        # 第一行通常是標題，但需要清理後綴
        title = lines[0] if lines else "無標題"
        for suffix in [' - 報導者 The Reporter', ' | 報導者', ' - 報導者']:
            if title.endswith(suffix):
                title = title[:-len(suffix)].strip()
        
        # 處理內文
        body_lines = []
        found_延伸閱讀 = False
        
        for i, line in enumerate(lines[1:], 1):  # 跳過第一行標題
            line = line.strip()
            if not line:
                continue
            
            # 檢查是否到達延伸閱讀區域
            # Reporter 的延伸閱讀通常以 "###" 開頭的標題開始
            if any(marker in line for marker in ReporterParser.STOP_MARKERS):
                found_延伸閱讀 = True
                break
            
            # 過濾日期格式的行 (如 "2019/11/12")
            if len(line) < 15 and '/' in line and line.replace('/', '').isdigit():
                continue
            
            # 過濾看起來像推薦文章標題的短行
            # Reporter 的推薦標題通常較短且不以句號結尾
            if len(line) < 100 and not line.endswith(('。', '！', '？', '」', '』', '、', '，')):
                # 如果已經遇到延伸閱讀標記，跳過短行
                if found_延伸閱讀:
                    continue
            
            body_lines.append(line)
        
        body = '\n'.join(body_lines)
        
        return title, body
