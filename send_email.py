'''import smtplib
import ssl
import certifi

context = ssl.create_default_context(cafile=certifi.where())

server = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context)
server.login("prithiyanga2368@gmail.com", "pqkk xane frfm aavy")
server.sendmail("prithiyanga2368@gmail.com", "prithiyanga2826@gmail.com", "Test Email")
server.quit()

print("Email Sent Successfully")'''
