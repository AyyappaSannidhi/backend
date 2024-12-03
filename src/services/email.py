from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from src.core.config import Config
from src.core.logging import logger

def send_email(receipient_email, subject, body):
    message = MIMEMultipart()
    message['From'] = Config.SENDER_EMAIL
    message['To'] = receipient_email
    message['Subject'] = subject
    
    # Attach the body as HTML
    message.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(Config.SENDER_EMAIL, Config.MAIL_APP_PASSWORD)
            server.sendmail(Config.SENDER_EMAIL, receipient_email, message.as_string())
            print('Email sent successfully!')
            return True
    except Exception as e:
        logger.info(f"Error: {str(e)}")
        return None
    
    