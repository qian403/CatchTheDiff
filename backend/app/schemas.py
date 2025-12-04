from pydantic import BaseModel
from typing import List

class NewsVersionBase(BaseModel):
    time: int
    title: str
    body: str

class NewsVersion(NewsVersionBase):
    id: int
    news_id: int

    class Config:
        from_attributes = True

class NewsBase(BaseModel):
    url: str
    source: int

class NewsCreate(NewsBase):
    normalized_id: str
    created_at: int
    last_fetch_at: int

class News(NewsBase):
    id: int
    created_at: int
    last_fetch_at: int
    last_changed_at: int
    error_count: int
    versions: List[NewsVersion] = []

    class Config:
        from_attributes = True
