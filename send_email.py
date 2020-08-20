import smtplib, ssl
from email.mime.text import MIMEText

class send_email:
    def __init__(self):
        pass
    def send(self, subject, messages):
        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        sender_email = "ryozheng123@gmail.com"  # Enter your address
        receiver_email = "royzhangzry@gmail.com"  # Enter receiver address
        password = 'ryoryogogogo123'
        SUBJECT = subject
        TEXT = messages
        message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)
