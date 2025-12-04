"""
新聞解析器模組

此模組包含各新聞來源的專用解析器，每個解析器負責：
1. 從 HTML 提取標題和內文
2. 過濾該來源特有的雜訊（廣告、推薦新聞等）
3. 處理該來源的 404 錯誤頁面

使用方式:
    from app.parsers import get_parser
    
    parser = get_parser(source_id)
    title, body = parser.parse(html)
"""

from typing import Type
from .base import NewsParser
from .rti import RtiParser
from .udn import UDNParser
from .cna import CNAParser
from .ettoday import EttodayParser
from .ltn import LibertytimesParser
from .reporter import ReporterParser
from .storm import StormParser

# 解析器映射表
# key: source_id, value: Parser class
PARSERS: dict[int, Type[NewsParser]] = {
    1: RtiParser,           # 中央廣播電台
    3: CNAParser,           # 中央社
    4: EttodayParser,       # ETtoday
    5: LibertytimesParser,  # 自由時報
    8: UDNParser,           # 聯合新聞網
    16: StormParser,        # 風傳媒
    18: ReporterParser,     # 報導者
}


def get_parser(source_id: int) -> Type[NewsParser]:
    """取得對應來源的解析器
    
    Args:
        source_id: 新聞來源 ID
        
    Returns:
        對應的解析器類別，若無專用解析器則回傳 NewsParser
    """
    return PARSERS.get(source_id, NewsParser)


# 匯出公開 API
__all__ = [
    'get_parser',
    'PARSERS',
    'NewsParser',
    'RtiParser',
    'UDNParser', 
    'CNAParser',
    'EttodayParser',
    'LibertytimesParser',
    'ReporterParser',
]
