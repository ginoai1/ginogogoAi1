import os
import time
import schedule
import subprocess
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / "config/.env")

SCRIPTS_DIR = Path(__file__).parent
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_DIR / "scheduler.log", "a") as f:
        f.write(line + "\n")

def run_file_organizer():
    log("執行：自動整理 Downloads 資料夾")
    result = subprocess.run(
        ["python3", str(SCRIPTS_DIR / "file_organizer.py")],
        capture_output=True, text=True
    )
    log(result.stdout.strip() or result.stderr.strip())

def run_web_summary():
    log("執行：每日新聞摘要")
    result = subprocess.run(
        ["python3", str(SCRIPTS_DIR / "web_scraper.py"), "https://news.ycombinator.com"],
        capture_output=True, text=True
    )
    log(result.stdout.strip())

def run_memory_monitor():
    log("執行：記憶體監控")
    result = subprocess.run(
        ["python3", str(SCRIPTS_DIR / "memory_monitor.py")],
        capture_output=True, text=True
    )
    log(result.stdout.strip())

# 排程設定
schedule.every().day.at("09:00").do(run_file_organizer)   # 每天早上 9 點整理檔案
schedule.every().day.at("08:00").do(run_web_summary)       # 每天早上 8 點新聞摘要
schedule.every(2).hours.do(run_memory_monitor)             # 每 2 小時檢查記憶體

if __name__ == "__main__":
    log("排程系統啟動")
    while True:
        schedule.run_pending()
        time.sleep(60)
