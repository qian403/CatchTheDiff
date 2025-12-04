"""
爬蟲基礎類別

定義所有爬蟲的統一介面
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List
from abc import ABC, abstractmethod


@dataclass
class NewsItem:
    """新聞項目資料結構"""
    url: str
    title: str
    published_at: datetime


class BaseCrawler(ABC):
    """爬蟲基礎類別
    
    所有爬蟲都應繼承此類別並實作 fetch_news_list() 方法
    """
    
    def __init__(self, source_id: int):
        """
        Args:
            source_id: 新聞來源 ID
        """
        self.source_id = source_id
    
    @abstractmethod
    async def fetch_news_list(self) -> List[NewsItem]:
        """獲取新聞列表
        
        Returns:
            NewsItem 列表，包含 url, title, published_at
        """
        raise NotImplementedError
    
    def get_source_id(self) -> int:
        """取得來源 ID"""
        return self.source_id
