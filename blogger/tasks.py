from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_login_success_email(email, username):
    subject = "Login Successful"
    message = f"Hello {username},\nYou have logged in successfully to Blog App."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)
    return "Mail sent"

@shared_task
def send_otp_email(email, otp):
    subject = "Your OTP for Blog App Login"
    message = f"Your OTP for login is: {otp}\nThis OTP is valid for 10 minutes."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)
    return "OTP sent"