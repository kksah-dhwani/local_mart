"""
Email test karne ke liye run karo:
  python test_email.py

Ye directly Gmail se email bhejega.
Agar error aaye to woh clearly print hoga.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# .env load karo
from dotenv import load_dotenv
load_dotenv()

from app.core.config import settings

print("=" * 50)
print("EMAIL CONFIG CHECK")
print("=" * 50)
print(f"MAIL_FROM    : {settings.MAIL_FROM or '❌ NOT SET'}")
print(f"MAIL_PASSWORD: {'✅ SET (' + str(len(settings.MAIL_PASSWORD)) + ' chars)' if settings.MAIL_PASSWORD else '❌ NOT SET'}")
print(f"MAIL_ADMIN   : {settings.MAIL_ADMIN or '❌ NOT SET'}")
print("=" * 50)

if not settings.MAIL_FROM or not settings.MAIL_PASSWORD or not settings.MAIL_ADMIN:
    print("\n❌ .env mein MAIL_FROM, MAIL_PASSWORD, MAIL_ADMIN set karo")
    sys.exit(1)

print("\nSending test email to admin...")

from app.services.email_service import send_email

try:
    send_email(
        to=settings.MAIL_ADMIN,
        subject="[LOCAL MART] ✅ Email Test Successful!",
        html_body="""
        <div style="font-family:Arial;padding:30px;max-width:400px;">
          <h2 style="color:#2563eb;">&#9989; Email is Working!</h2>
          <p>Your Local Mart email configuration is working correctly.</p>
          <p style="color:#64748b;font-size:13px;">
            MAIL_FROM: """ + settings.MAIL_FROM + """<br>
            MAIL_ADMIN: """ + settings.MAIL_ADMIN + """
          </p>
        </div>
        """
    )
    print(f"\n✅ SUCCESS! Test email sent to {settings.MAIL_ADMIN}")
    print("Inbox check karo (Spam folder bhi dekho)")

except Exception as e:
    print(f"\n❌ FAILED: {e}")
    print("\nCommon fixes:")
    print("1. Gmail App Password use karo (normal password nahi chalega)")
    print("2. Google Account > Security > 2-Step Verification > App Passwords")
    print("3. MAIL_PASSWORD mein spaces mat daalo")
