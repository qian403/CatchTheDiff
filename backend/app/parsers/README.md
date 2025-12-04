# 新聞解析器開發指南

本資料夾包含各新聞來源的專用解析器。

## 檔案結構

```
parsers/
├── __init__.py    # 模組入口，匯出 get_parser()
├── base.py        # NewsParser 基礎類別
├── rti.py         # 中央廣播電台
├── udn.py         # 聯合新聞網
├── cna.py         # 中央社
├── ettoday.py     # ETtoday
├── ltn.py         # 自由時報
└── README.md      # 本說明文件
```

## 新增解析器

1. 在 `parsers/` 建立新檔案，例如 `tvbs.py`
2. 繼承 `NewsParser` 並實作 `parse()` 方法
3. 在 `__init__.py` 的 `PARSERS` 字典中註冊

### 範例

```python
# parsers/tvbs.py
from bs4 import BeautifulSoup
from typing import Tuple
from .base import NewsParser


class TVBSParser(NewsParser):
    """TVBS 解析器"""
    
    # 定義該來源特有的停止標記
    STOP_MARKERS = ['延伸閱讀', '看更多']
    
    @staticmethod
    def parse(html: str) -> Tuple[str, str]:
        soup = BeautifulSoup(html, "html.parser")
        
        # 1. 提取標題
        title_elem = soup.find("h1")
        title = title_elem.get_text(strip=True) if title_elem else "無標題"
        
        # 2. 提取內文
        body_elem = soup.find("div", {"class": "article-content"})
        if body_elem:
            # 移除無關元素
            for unwanted in body_elem.find_all(["script", "style"]):
                unwanted.decompose()
            
            # 過濾雜訊
            lines = body_elem.get_text(separator="\\n").split("\\n")
            cleaned = []
            for line in lines:
                line = line.strip()
                if any(m in line for m in TVBSParser.STOP_MARKERS):
                    break
                cleaned.append(line)
            
            body = "\\n".join(cleaned)
        else:
            body = "無法取得內文"
        
        return title, body
```

然後在 `__init__.py` 註冊：

```python
from .tvbs import TVBSParser

PARSERS = {
    # ... 現有的 ...
    9: TVBSParser,  # TVBS
}
```

## 注意事項

- 每個解析器應該獨立運作，不依賴其他解析器
- 使用類別常數定義停止標記和雜訊模式，方便維護
- 處理 404 頁面，回傳 `("404", "404")`
- 內文找不到時回傳 `"無法取得內文"`
