"""
中時新聞網爬蟲

使用 DrissionPage 爬取中時新聞網的新聞列表和內容
"""
from DrissionPage import ChromiumPage, ChromiumOptions
from typing import List, Dict, Optional
import time

class ChinatimesCrawler:
    """中時新聞網爬蟲"""
    
    BASE_URL = "https://www.chinatimes.com"
    REALTIME_URL = "https://www.chinatimes.com/realtimenews/?chdtv"
    
    def __init__(self, headless: bool = True):
        """
        初始化爬蟲
        
        Args:
            headless: 是否安裝無頭模式
        """
        co = ChromiumOptions()
        if headless:
            co.headless()
        
        # 設置 User-Agent
        co.set_user_agent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        # 自動尋找可用端口
        co.auto_port()
        
        try:
            self.page = ChromiumPage(co)
        except Exception as e:
            print(f"⚠️  無法啟動瀏覽器: {e}")
            print("提示：請確保系統已安裝 Chrome 或 Chromium")
            raise
    
    def get_news_list(self, limit: int = 20) -> List[str]:
        """
        從即時新聞頁面獲取新聞 URL 列表
        
        Args:
            limit: 最多獲取幾則新聞
            
        Returns:
            新聞 URL 列表
        """
        print(f"📰 正在訪問中時新聞網...")
        self.page.get(self.REALTIME_URL)
        
        # 等待頁面載入
        time.sleep(2)
        
        # 查找新聞鏈接
        # 中時的實際新聞鏈接格式為 /realtimenews/YYYYMMDDNUMBER-CATEGORY
        # 使用 CSS 選擇器查找符合此模式的鏈接
        news_urls = []
        
        # 查找所有鏈接，篩選實際新聞（包含日期碼）
        links = self.page.eles('css:a[href^="/realtimenews/202"]')
        
        for link in links:
            href = link.attr('href')
            if href:
                # 補完網址
                if href.startswith('/'):
                    full_url = self.BASE_URL + href
                else:
                    full_url = href
                
                # 去掉 query string
                if '?' in full_url:
                    full_url = full_url.split('?')[0]
                
                # 去重
                if full_url not in news_urls:
                    news_urls.append(full_url)
                    
                    if len(news_urls) >= limit:
                        break
        
        print(f"✅ 找到 {len(news_urls)} 則新聞")
        return news_urls
    
    def extract_article(self, url: str) -> Optional[Dict[str, str]]:
        """
        從新聞頁面提取標題和內文
        
        Args:
            url: 新聞 URL
            
        Returns:
            包含 title 和 body 的字典，如果失敗則返回 None
        """
        try:
            print(f"📄 正在提取: {url}")
            self.page.get(url)
            time.sleep(1.5)
            
            # 提取標題 - 中時新聞的標題在 h1 標籤中
            title_ele = self.page.ele('tag:h1')
            title = title_ele.text if title_ele else ""
            
            # 清理標題中的後綴（如 "- 生活 - 中時"）
            if title and ' - ' in title:
                # 保留第一部分（實際標題）
                title = title.split(' - ')[0].strip()
            
            # 提取內文 - 專門針對中時新聞的文章主體
            body = ""
            body_parts = []
            
            # 使用精確選擇器：div.article-body
            article_div = self.page.ele('css:.article-body', timeout=2)
            if article_div:
                # Get raw HTML to check for comment markers
                article_html = article_div.html
                
                # Stop at sponsorship/ad markers
                if '<!--文章贊助' in article_html or '<!--文末影音廣告' in article_html:
                    # Split at the comment and only take content before it
                    stop_markers = ['<!--文章贊助', '<!--文末影音廣告']
                    for marker in stop_markers:
                        if marker in article_html:
                            article_html = article_html.split(marker)[0]
                            break
                
                # 取得所有段落
                paragraphs = article_div.eles('tag:p')
                
                stop_extraction = False
                
                for p in paragraphs:
                    # Check if this paragraph's HTML contains ad markers
                    p_html = p.html
                    if '<!--文章贊助' in p_html or '<!--文末影音廣告' in p_html:
                        stop_extraction = True
                        break
                    
                    text = p.text
                    
                    # Stop at "文章來源：" - this marks end of article
                    if '文章來源：' in text or '贊助本文章' in text:
                        stop_extraction = True
                        break
                    
                    if not text or len(text.strip()) < 20:
                        continue
                    
                    text = text.strip()
                    
                    # 過濾掉不需要的內容
                    # 1. 推薦閱讀類
                    if any(keyword in text for keyword in [
                        '延伸閱讀', '更多新聞', '相關新聞', '推薦閱讀', '也許您會感興趣',
                        '熱門新聞', '即時熱門', '今日熱門'
                    ]):
                        continue
                    
                    # 2. 標籤和分類（通常是 # 開頭或很短）
                    if text.startswith('#') or text.startswith('【'):
                        continue
                    
                    # 3. 導航和UI元素
                    if any(keyword in text for keyword in [
                        '►►', '※', '★', '●', '■', '▲',
                        '訂閱', '加入', '追蹤', '下載APP', '會員', '登入',
                        '複製連結', '字級設定', '發表意見', '留言規則', '關閉', '回到頁首'
                    ]):
                        continue
                    
                    # 檢查社交分享按鈕（更精確）
                    if len(text) < 50 and any(keyword in text for keyword in ['Facebook', 'Line', 'Threads']):
                        if '分享' in text or 'Share' in text:
                            continue
                    
                    # 4. 廣告和活動
                    if any(keyword in text for keyword in [
                        '豔陽映照', '精選', '活動', '燦爛綻放',
                        '中時新聞網對留言', '請勿', '禁止發表',
                        '贊助', '支持', 'LINE Pay', 'Google Pay', 'Apple Pay'
                    ]):
                        continue
                    
                    # 5. 影片節目推廣（新增）
                    if any(keyword in text for keyword in [
                        '頭條開講', 'This is a modal window', '第', '集'
                    ]) and len(text) > 30:
                        # 檢查是否看起來像節目標題
                        if '集' in text or 'modal' in text.lower():
                            continue
                    
                    # 6. 推薦新聞標題（短文且看起來像標題）
                    # 檢查是否為推薦文章標題：短且包含特定模式
                    if len(text) < 80:
                        # 常見的推薦文章標題模式
                        title_patterns = [
                            '利特投手', '神童激動', '全智賢', '韓劇',
                            '來勢洶洶', '穩定幣', '何時上路', '超調皮', '爆笑畫面',
                            '全場嗨翻', '陷抹黑爭議', '開球', '批'
                        ]
                        # 如果是短文且包含這些模式，且沒有句號結尾，很可能是標題
                        if any(pattern in text for pattern in title_patterns):
                            if not text.endswith('。') and not text.endswith('！') and not text.endswith('？'):
                                continue
                    
                    # 7. 其他短新聞標題
                    if len(text) < 50 and any(keyword in text for keyword in [
                        '來勢洶洶', '穩定幣', '何時上路', '超調皮', '爆笑畫面'
                    ]):
                        continue
                    
                    # 8. 時間戳記和作者信息（過短的段落）
                    if len(text) < 30 and any(char in text for char in '/:：'):
                        continue
                    
                    # Stop if we hit the marker
                    if stop_extraction:
                        break
                    
                    body_parts.append(text)
            
            # 組合內文
            if body_parts:
                body = '\n\n'.join(body_parts)
            
            # 驗證內容質量
            if title and body and len(body) > 100:
                # 最終檢查：使用嚴格的段落過濾
                lines = body.split('\n')
                clean_lines = []
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 嚴格過濾：只保留真正的文章段落
                    # 1. 最小長度要求 (放寬到 25 字)
                    if len(line) < 25:
                        continue
                    
                    # 2. 必須以正確的標點符號結尾
                    if not line.endswith(('。', '？', '！', '）', '」', '』', '.')):
                        continue
                    
                    # 3. 檢查是否為推薦文章標題（短文且有特定關鍵詞）
                    if len(line) < 100:
                        title_keywords = ['曝光', '爆', '控訴', '被逮', '慘被', '暴漲', '示警']
                        has_keyword = any(kw in line for kw in title_keywords)
                        has_quotes = '「' in line or '《' in line or '"' in line
                        
                        if has_keyword and has_quotes:
                            # 很可能是推薦標題
                            continue
                    
                    clean_lines.append(line)
                
                body = '\n'.join(clean_lines)
                
                # 確保最終內容足夠且合理
                if len(body) > 100 and len(body) < 50000:
                    return {
                        'title': title.strip(),
                        'body': body.strip()
                    }
                else:
                    print(f"  ⚠️  內容長度不合理: {len(body)} 字")
                    return None
            else:
                print(f"  ⚠️  無法提取完整內容 (標題: {len(title) if title else 0}, 內文: {len(body) if body else 0})")
                return None
                
        except Exception as e:
            print(f"  ❌ 提取失敗: {e}")
            return None
    
    def close(self):
        """關閉瀏覽器"""
        if self.page:
            self.page.quit()

def test_crawler():
    """測試爬蟲功能"""
    print("="*70)
    print("測試中時新聞網爬蟲")
    print("="*70)
    print()
    
    crawler = ChinatimesCrawler(headless=True)
    
    try:
        # 測試 1: 獲取新聞列表
        print("測試 1: 獲取新聞列表")
        print("-"*70)
        urls = crawler.get_news_list(limit=5)
        
        for i, url in enumerate(urls, 1):
            print(f"{i}. {url}")
        
        print()
        
        # 測試 2: 提取第一則新聞內容
        if urls:
            print("測試 2: 提取新聞內容")
            print("-"*70)
            article = crawler.extract_article(urls[0])
            
            if article:
                print(f"標題: {article['title']}")
                print(f"內文長度: {len(article['body'])} 字")
                print(f"內文預覽: {article['body'][:200]}...")
            else:
                print("提取失敗")
        
        print()
        print("="*70)
        print("測試完成")
        print("="*70)
        
    finally:
        crawler.close()

if __name__ == "__main__":
    test_crawler()
