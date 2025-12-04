"""
爬蟲執行腳本
用法: uv run run_crawler.py <url>
"""
import asyncio
import sys
from app import database, crawler

async def main():
    if len(sys.argv) < 2:
        print("用法: uv run run_crawler.py <url>")
        return

    url = sys.argv[1]
    
    async with database.AsyncSessionLocal() as db:
        await crawler.process_news(db, url, source_id=1)

if __name__ == "__main__":
    asyncio.run(main())
