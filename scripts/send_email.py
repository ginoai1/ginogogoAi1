import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from dotenv import load_dotenv
import anthropic

load_dotenv(dotenv_path=Path(__file__).parent.parent / "config/.env")

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def ai_compose_email(topic: str, recipient_name: str) -> dict:
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[{"role": "user", "content": f"請用繁體中文寫一封關於「{topic}」的專業 email 給 {recipient_name}。回覆格式：\n主旨：...\n內容：..."}]
    )
    text = msg.content[0].text
    lines = text.strip().split("\n")
    subject = lines[0].replace("主旨：", "").strip()
    body = "\n".join(lines[2:]).replace("內容：", "").strip()
    return {"subject": subject, "body": body}

def send_email(to: str, subject: str, body: str):
    from_addr = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")

    msg = MIMEMultipart()
    msg["From"] = from_addr
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(from_addr, password)
        server.send_message(msg)
    print(f"Email 已發送至 {to}")

if __name__ == "__main__":
    result = ai_compose_email("明天的會議時間確認", "客戶")
    print(f"主旨：{result['subject']}")
    print(f"內容：{result['body']}")
    # 確認後取消註解發送
    # send_email("收件人@gmail.com", result["subject"], result["body"])
