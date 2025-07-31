def send_email(to_email: str, subject: str, body: str):
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = "noreply@your-domain.local"
        msg["To"] = to_email
        msg.set_content(body)

        with smtplib.SMTP("localhost") as server:
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"[!] Ошибка отправки email: {e}")
        return False
