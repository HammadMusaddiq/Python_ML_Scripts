import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

import getpass
import os

# Variables that will be used to send an email
subject = "Email from Python"
msg_content = "This is an email with attachment sent from Python"
sender_email = "hammadmusaddiq17@gmail.com"
receiver_email = ["hammadmusaddiq@g"] # you can add multiple emails in this list using comma's in bettween
cc_email = []
bcc_email = []
password_email = getpass.getpass("Please enter email password: ")  #Here put pasword to your eventim login email. 

path_to_folder = '/home/hammad/Downloads/Email_Temp/' 

def attatchment_files():
    file_names = [f for f in os.listdir(path_to_folder) if os.path.isfile(os.path.join(path_to_folder, f))]
    print(file_names)
    return file_names

def Email():
    # Create a multipart message and set headers
    message = MIMEMultipart('mixed')
    message['From'] = sender_email
    message['To'] = ", ".join(receiver_email)
    message['CC'] = ", ".join(cc_email)
    message['Bcc'] = ", ".join(bcc_email)
    message['Subject'] = subject

    body = MIMEText(msg_content, 'html')
    message.attach(body)

    # file_names = ['/home/hammad/Downloads/Muhammad_Hammad Musaddiq_Resume_18-01-2023-14-36-18.pdf']
    file_names = attatchment_files()

    try:
        for path in file_names:  # add files to the message
            file_path = os.path.join(path_to_folder, path)
            file_type = path.split('.')[-1]
            attachment = MIMEApplication(open(file_path, "rb").read(), _subtype = file_type) 
            attachment.add_header('Content-Disposition','attachment', filename = path)
            message.attach(attachment)
            
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password_email)
            server.sendmail(sender_email, receiver_email + cc_email + bcc_email, message.as_string())

        print("email sent out successfully")
        
    except Exception as E:
        print(E)


if __name__ == "__main__":
    Email()