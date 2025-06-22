import smtplib

smtp_server = "smtp.gmail.com"
smtp_port = 465
smtp_username = "epatnor@gmail.com"
smtp_password = "ebxkozpuvxpvgauq"

try:
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(smtp_username, smtp_password)
        print("SMTP login success!")
except Exception as e:
    print("SMTP login failed:", e)
