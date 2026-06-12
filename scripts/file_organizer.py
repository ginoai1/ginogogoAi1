import os
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import anthropic

load_dotenv(dotenv_path=Path(__file__).parent.parent / "config/.env")

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# 用 dict 加速副檔名查找（O(1) vs 原本 O(n)）
EXT_TO_FOLDER = {ext: folder for folder, exts in {
    "圖片": [".jpg", ".jpeg", ".png", ".gif", ".heic", ".webp"],
    "文件": [".pdf", ".doc", ".docx", ".txt", ".pages"],
    "試算表": [".xls", ".xlsx", ".csv", ".numbers"],
    "影片": [".mp4", ".mov", ".avi", ".mkv"],
    "音樂": [".mp3", ".m4a", ".wav", ".flac"],
    "壓縮檔": [".zip", ".tar", ".gz", ".rar"],
    "程式碼": [".py", ".js", ".ts", ".html", ".css", ".json"],
    "安裝檔": [".dmg", ".pkg", ".iso", ".app", ".exe", ".msi"],
    "設定檔": [".conf", ".cfg", ".ini", ".yaml", ".yml"],
}.items() for ext in exts}

def _move_file(args):
    file, dest_dir = args
    dest_dir.mkdir(exist_ok=True)
    shutil.move(str(file), str(dest_dir / file.name))
    return f"{file.name} → {dest_dir.name}/"

def organize_folder(target_dir: str):
    target = Path(target_dir)
    tasks = []

    for file in target.iterdir():
        if file.is_dir():
            continue
        folder_name = EXT_TO_FOLDER.get(file.suffix.lower())
        if folder_name:
            tasks.append((file, target / folder_name))

    if not tasks:
        print("沒有需要整理的檔案。")
        return

    # 多執行緒同時移動檔案
    with ThreadPoolExecutor(max_workers=4) as executor:
        moved = list(executor.map(_move_file, tasks))

    summary = "\n".join(moved)
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[{"role": "user", "content": f"以下檔案已整理完成，請用繁體中文簡短摘要：\n{summary}"}]
    )
    print(msg.content[0].text)

if __name__ == "__main__":
    import sys
    folder = sys.argv[1] if len(sys.argv) > 1 else str(Path.home() / "Downloads")
    print(f"整理資料夾：{folder}")
    organize_folder(folder)
