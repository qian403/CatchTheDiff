from sqlalchemy import Column, Integer, String, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base

class News(Base):
    """新聞資料表"""
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    normalized_id = Column(String, index=True)
    source = Column(Integer, index=True)
    created_at = Column(Integer)
    last_fetch_at = Column(Integer)
    last_changed_at = Column(Integer, default=0)
    error_count = Column(Integer, default=0)

    versions = relationship("NewsVersion", back_populates="news", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_source_created', 'source', 'created_at'),
        Index('idx_source_changed', 'source', 'last_changed_at'),
    )

class NewsVersion(Base):
    """新聞版本資料表"""
    __tablename__ = "news_versions"

    id = Column(Integer, primary_key=True, index=True)
    news_id = Column(Integer, ForeignKey("news.id"), index=True)
    time = Column(Integer, index=True)
    title = Column(String, index=True)  # Add index for search
    body = Column(Text)

    news = relationship("News", back_populates="versions")
