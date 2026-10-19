import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.header import Header
import datetime




def send_email(subject, image_path, sender_email, sender_password, recipient_email, smtp_server, smtp_port):
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()
        server.starttls()
        server.login(sender_email, sender_password)
        #msg = MIMEText(message)
        
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email
        with open(image_path, "rb") as f:
            img_data = f.read()
        img = MIMEImage(img_data, name=os.path.basename(image_path))
        msg.attach(img)
        server.send_message(msg)
        server.quit()
        print('Email sent successfully!')
    except smtplib.SMTPException as e:
        print(f"Error: Email could not be sent. {e}")

if __name__ == '__main__':

    subject =  "Statistik Atemerkennung"
    #message = "Noch funktioniert es"
    image_path = ""
    sender_email = ""
    sender_password = ""
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    recipient_email = ""
    send_email(subject, image_path, sender_email, sender_password, recipient_email, smtp_server, smtp_port)
