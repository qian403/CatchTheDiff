"""
RSS Feed 配置

定義各新聞來源的 RSS Feed 網址
"""

from app.google_news import get_media_google_news_feeds

# 各新聞來源的 RSS Feed
RSS_FEEDS = {
    1: [  # 中央廣播電台 (使用官方 RSS)
        "https://www.rti.org.tw/rss",  # 新聞總覽
    ],
    2: get_media_google_news_feeds(2),  # 中時新聞網 (透過 Google News)
    3: [  # 中央社 (使用官方 FeedBurner)
        "https://feeds.feedburner.com/rsscna/politics",     # 政治
        "https://feeds.feedburner.com/rsscna/intworld",     # 國際
        "https://feeds.feedburner.com/rsscna/mainland",     # 兩岸
        "https://feeds.feedburner.com/rsscna/finance",      # 產經證券
        "https://feeds.feedburner.com/rsscna/technology",   # 科技
        "https://feeds.feedburner.com/rsscna/lifehealth",   # 生活
        "https://feeds.feedburner.com/rsscna/social",       # 社會
        "https://feeds.feedburner.com/rsscna/local",        # 地方
        "https://feeds.feedburner.com/rsscna/culture",      # 文化
        "https://feeds.feedburner.com/rsscna/sport",        # 運動
        "https://feeds.feedburner.com/rsscna/stars",        # 娛樂
    ],
    4: [  # ETtoday (使用官方 Feedburner)
        "https://feeds.feedburner.com/ettoday/realtime",  # 即時新聞
        "https://feeds.feedburner.com/ettoday/politics",  # 政治
        "https://feeds.feedburner.com/ettoday/finance",   # 財經
    ],
    5: [  # 自由時報 (使用官方 RSS)
        "https://news.ltn.com.tw/rss/all.xml",          # 所有新聞
        "https://news.ltn.com.tw/rss/focus.xml",        # 焦點新聞  
        "https://news.ltn.com.tw/rss/politics.xml",     # 政治
        "https://news.ltn.com.tw/rss/society.xml",      # 社會
        "https://news.ltn.com.tw/rss/local.xml",        # 地方
    ],
    6: get_media_google_news_feeds(6),   # 新頭殼 (透過 Google News)
    7: get_media_google_news_feeds(7),   # NOWnews (透過 Google News)
    8: get_media_google_news_feeds(8),   # 聯合新聞網 (透過 Google News)
    9: get_media_google_news_feeds(9),   # TVBS (透過 Google News)
    10: get_media_google_news_feeds(10), # 中廣新聞網 (透過 Google News)
    11: get_media_google_news_feeds(11), # 公視新聞網 (透過 Google News)
    12: get_media_google_news_feeds(12), # 台視新聞 (透過 Google News)
    13: get_media_google_news_feeds(13), # 華視新聞 (透過 Google News)
    14: get_media_google_news_feeds(14), # 民視新聞 (透過 Google News)
    15: get_media_google_news_feeds(15), # 三立新聞 (透過 Google News)
    16: [  # 風傳媒 (使用官方 RSS)
        "https://www.storm.mg/api/getRss/channel_id/2?path=https://www.storm.mg/article",
    ],
    17: get_media_google_news_feeds(17), # 關鍵評論網 (透過 Google News)
    18: [  # 報導者 (使用官方 RSS)
        "https://public.twreporter.org/rss/twreporter-rss.xml",  # 新聞總覽
    ],
}

def get_rss_feeds(source_id: int = None):
    """取得 RSS Feeds"""
    if source_id is None:
        # 回傳所有 feeds
        all_feeds = []
        for sid, feeds in RSS_FEEDS.items():
            for feed in feeds:
                all_feeds.append((sid, feed))
        return all_feeds
    return [(source_id, feed) for feed in RSS_FEEDS.get(source_id, [])]
