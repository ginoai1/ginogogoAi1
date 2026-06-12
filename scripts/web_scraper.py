import os
import requests
from pathlib import Path
from dotenv import load_dotenv
from functools import lru_cache
import anthropic

load_dotenv(dotenv_path=Path(__file__).parent.parent / "config/.env")

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

@lru_cache(maxsize=32)
def scrape_and_summarize(url: str) -> str:
    try:
        from urllib.request import urlopen
        from html.parser import HTMLParser

        class TextExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text = []
                self.skip = False
            def handle_starttag(self, tag, attrs):
                if tag in ("script", "style", "nav", "footer"):
                    self.skip = True
            def handle_endtag(self, tag):
                if tag in ("script", "style", "nav", "footer"):
                    self.skip = False
            def handle_data(self, data):
                if not self.skip and data.strip():
                    self.text.append(data.strip())

        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urlopen(url, timeout=10, context=ctx) as response:
            html = response.read().decode("utf-8", errors="ignore")

        parser = TextExtractor()
        parser.feed(html)
        content = " ".join(parser.text)[:3000]

        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            messages=[{"role": "user", "content": f"請用繁體中文摘要以下網頁內容（3-5句話）：\n{content}"}]
        )
        return msg.content[0].text

    except Exception as e:
        return f"錯誤：{e}"

if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else "https://news.ycombinator.com"
    print(f"分析網頁：{url}")
    print(scrape_and_summarize(url))
