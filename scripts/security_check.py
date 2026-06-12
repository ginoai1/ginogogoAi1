import subprocess
import os
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

def run(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL, text=True).strip()
    except:
        return "無法取得"

def check():
    results = []
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    results.append(f"資安檢查報告 {ts}\n{'='*40}")

    checks = [
        ("防火牆", "/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate"),
        ("FileVault", "fdesetup status"),
        ("Gatekeeper", "spctl --status"),
        ("SIP", "csrutil status"),
        ("SSH 服務", "launchctl list com.openssh.sshd 2>/dev/null || echo '未啟動'"),
        ("螢幕鎖定", "defaults read com.apple.screensaver askForPassword"),
        ("開放連接埠", "netstat -an | grep LISTEN | grep -v '127.0.0.1' | grep -v '::1' | wc -l"),
    ]

    for name, cmd in checks:
        result = run(cmd)
        status = "✅" if any(k in result for k in ["enabled", "On", "1", "未啟動"]) else "⚠️"
        results.append(f"{status} {name}: {result}")

    report = "\n".join(results)
    print(report)

    with open(LOG_DIR / "security.log", "a") as f:
        f.write(report + "\n\n")

if __name__ == "__main__":
    check()
