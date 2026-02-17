import random
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings

def send_email_otp(user):
    otp = str(random.randint(100000, 999999))
    
    # Handle different models having different field names
    if hasattr(user, 'email_otp'):
        user.email_otp = otp
    elif hasattr(user, 'otp'):
        user.otp = otp
        
    if hasattr(user, 'otp_created_at'):
        user.otp_created_at = timezone.now()
        
    user.save()

    try:
        send_mail(
            "Verify your email",
            f"Your verification code is {otp}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
    except Exception as e:
        print("Email error:", e)

