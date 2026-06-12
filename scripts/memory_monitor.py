import subprocess
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / "config/.env")

LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

def get_memory_stats():
    swap = subprocess.check_output("sysctl vm.swapusage", shell=True, text=True).strip()
    pressure = subprocess.check_output("memory_pressure | grep 'free percentage'", shell=True, text=True).strip()
    swap_used = float(swap.split("used = ")[1].split("M")[0])
    free_pct = int(pressure.split(": ")[1].replace("%", ""))
    return swap_used, free_pct

def get_top_processes():
    out = subprocess.check_output(
        "ps axo rss,comm | sort -rn | head -6 | tail -5",
        shell=True, text=True
    )
    lines = []
    for line in out.strip().split("\n"):
        parts = line.split(None, 1)
        if len(parts) == 2:
            mb = int(parts[0]) / 1024
            name = parts[1].split("/")[-1][:40]
            lines.append(f"  {mb:.0f}MB  {name}")
    return "\n".join(lines)

def cleanup_caches():
    freed = []
    try:
        subprocess.run("pip3 cache purge", shell=True, capture_output=True)
        freed.append("pip 快取")
    except:
        pass
    try:
        subprocess.run("brew cleanup --prune=7 -q", shell=True, capture_output=True)
        freed.append("Homebrew 快取")
    except:
        pass
    return "、".join(freed) if freed else "無"

def monitor():
    from datetime import datetime
    swap_used, free_pct = get_memory_stats()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")

    status = "🔴 危險" if free_pct < 20 else "🟡 偏低" if free_pct < 40 else "🟢 正常"
    report = (
        f"[{ts}] 記憶體狀態：{status}\n"
        f"  可用記憶體：{free_pct}%\n"
        f"  Swap 使用：{swap_used:.0f} MB\n"
        f"前5大佔用程序：\n{get_top_processes()}"
    )

    print(report)

    with open(LOG_DIR / "memory.log", "a") as f:
        f.write(report + "\n\n")

    # 記憶體低於 25% 時自動清理快取
    if free_pct < 25:
        print(f"\n⚠️  記憶體不足，自動清理快取...")
        freed = cleanup_caches()
        print(f"已清理：{freed}")

if __name__ == "__main__":
    monitor()
