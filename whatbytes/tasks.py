from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_password_reset_email(subject, email_content, recipient_email):
    try:
        send_mail(subject, email_content, 'guptamanish1006@gmail.com', [recipient_email])
        print(f"Email sent to {recipient_email}")
    except Exception as e:
        print(f"Failed to send email to {recipient_email}. Error: {e}")
