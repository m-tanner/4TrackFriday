def send_email(request):
    import os
    import smtplib
    from email.message import EmailMessage

    smtp_obj = smtplib.SMTP("smtp.mail.me.com", 587)
    smtp_obj.starttls()
    smtp_obj.login(
        os.environ["FTF_EMAIL_ADDRESS"], os.environ["FTF_EMAIL_PASSWORD"]
    )

    msg = EmailMessage()
    msg["Subject"] = request.values["Subject"]
    msg["From"] = smtp_obj.user
    msg["To"] = request.values["To"]
    msg.set_content(request.values["Body"], subtype="html")

    smtp_obj.send_message(msg=msg)
    smtp_obj.quit()

    return f"Email sent to {request.values['To']}!", 200
