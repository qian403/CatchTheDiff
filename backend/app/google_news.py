"""
Google News RSS Feed 生成器

為沒有官方 RSS 的新聞媒體生成 Google News RSS feed URL
"""

def get_google_news_rss(domain: str, topic: str = None) -> str:
    """
    生成 Google News RSS feed URL
    
    Args:
        domain: 新聞網站域名 (例如: tvbs.com.tw)
        topic: 可選的主題關鍵字
    
    Returns:
        Google News RSS feed URL
    """
    base_url = "https://news.google.com/rss/search"
    
    # 構建搜尋查詢
    if topic:
        query = f"site:{domain} {topic}"
    else:
        query = f"site:{domain}"
    
    # 台灣繁體中文設定
    params = f"?q={query}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    
    return base_url + params

# 各媒體的域名對應
MEDIA_DOMAINS = {
    1: "rti.org.tw",             # 中央廣播電台
    2: "chinatimes.com",         # 中時新聞網
    6: "newtalk.tw",             # 新頭殼
    7: "nownews.com",            # NOWnews今日新聞
    8: "udn.com",                # 聯合新聞網
    9: "tvbs.com.tw",            # TVBS新聞
    10: "bcc.com.tw",            # 中廣新聞網
    11: "pts.org.tw",            # 公視新聞網
    12: "ttv.com.tw",            # 台視新聞
    13: "cts.com.tw",            # 華視新聞
    14: "ftvnews.com.tw",        # 民視新聞
    15: "setn.com",              # 三立新聞
    16: "storm.mg",              # 風傳媒
    17: "thenewslens.com",       # 關鍵評論網
}

def get_media_google_news_feeds(source_id: int, topics: list = None) -> list:
    """
    為特定媒體生成 Google News RSS feeds
    
    Args:
        source_id: 媒體來源 ID
        topics: 主題列表（可選）
    
    Returns:
        RSS feed URLs 列表
    """
    domain = MEDIA_DOMAINS.get(source_id)
    if not domain:
        return []
    
    if topics:
        return [get_google_news_rss(domain, topic) for topic in topics]
    else:
        # 如果沒有指定主題，回傳該媒體的所有新聞
        return [get_google_news_rss(domain)]
