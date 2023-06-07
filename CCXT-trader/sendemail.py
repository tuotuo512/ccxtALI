import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(subject, message, to_email):
    # 发件人邮箱
    from_email = 'your_email@example.com'
    # 发件人邮箱密码或授权码
    password = 'your_password'

    # 连接SMTP服务器并发送邮件
    with smtplib.SMTP('smtp.example.com', 587) as server:
        server.starttls()
        server.login('your_username', 'your_password')
        email = f"Subject: {subject}\n\n{message}"

# 调用 send_email 函数发送邮件
subject = 'Test Email'
message = 'Hello, this is a test email.'
to_email = '410660480@qq.com'
send_email(subject, message, to_email)

