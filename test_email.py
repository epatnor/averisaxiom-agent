import smtplib

smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_username = "epatnor@gmail.com"
smtp_password = "ebxkozpuvxpvgauq"

try:
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_username, smtp_password)
        print("SMTP login success!")
except Exception as e:
    print("SMTP login failed:", e)
