"""
Email Service - Handles OTP generation, sending, and verification via SMTP.
Uses Python's built-in smtplib (no extra dependencies needed).
"""
import random
import smtplib
import datetime
import sys
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database.db_connection import db
from config.settings import settings


OTP_EXPIRY_MINUTES = 10


def generate_otp() -> str:
    """Generate a cryptographically safe 6-digit OTP."""
    return str(random.SystemRandom().randint(100000, 999999))


def send_otp_email(to_email: str, otp: str, purpose: str = 'verify') -> bool:
    """
    Send an OTP email to the farmer.
    purpose: 'verify' for email verification, 'reset' for password reset.
    Returns True on success, False on failure.
    """
    if purpose == 'reset':
        subject = "🔑 Password Reset OTP - Agri-AI"
        body_html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 480px; margin: auto; background: #f9f9f9; border-radius: 12px; overflow: hidden;">
          <div style="background: linear-gradient(135deg, #2e7d32, #4caf50); padding: 32px; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 26px;">🌾 Agri-AI</h1>
            <p style="color: #c8e6c9; margin: 8px 0 0 0;">AI Crop Diagnosis System</p>
          </div>
          <div style="padding: 32px; background: white;">
            <h2 style="color: #2e7d32; margin-top: 0;">Password Reset Request</h2>
            <p style="color: #555; line-height: 1.6;">We received a request to reset your password. Use the OTP below to create a new password.</p>
            <div style="background: #e8f5e9; border-radius: 12px; padding: 24px; text-align: center; margin: 24px 0;">
              <p style="color: #555; margin: 0 0 8px 0; font-size: 14px;">Your One-Time Password</p>
              <span style="font-size: 40px; font-weight: bold; color: #2e7d32; letter-spacing: 10px;">{otp}</span>
            </div>
            <p style="color: #888; font-size: 13px;">⏰ This OTP is valid for <strong>{OTP_EXPIRY_MINUTES} minutes</strong>.</p>
            <p style="color: #888; font-size: 13px;">If you did not request this, please ignore this email. Your password will remain unchanged.</p>
          </div>
          <div style="padding: 16px; background: #f0faf0; text-align: center;">
            <p style="color: #aaa; font-size: 12px; margin: 0;">© 2026 Agri-AI — AI Crop Diagnosis System</p>
          </div>
        </div>
        """
    else:
        subject = "✅ Email Verification OTP - Agri-AI"
        body_html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 480px; margin: auto; background: #f9f9f9; border-radius: 12px; overflow: hidden;">
          <div style="background: linear-gradient(135deg, #2e7d32, #4caf50); padding: 32px; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 26px;">🌾 Agri-AI</h1>
            <p style="color: #c8e6c9; margin: 8px 0 0 0;">AI Crop Diagnosis System</p>
          </div>
          <div style="padding: 32px; background: white;">
            <h2 style="color: #2e7d32; margin-top: 0;">Verify Your Email</h2>
            <p style="color: #555; line-height: 1.6;">Welcome to Agri-AI! Please verify your email address to activate your account.</p>
            <div style="background: #e8f5e9; border-radius: 12px; padding: 24px; text-align: center; margin: 24px 0;">
              <p style="color: #555; margin: 0 0 8px 0; font-size: 14px;">Your Verification Code</p>
              <span style="font-size: 40px; font-weight: bold; color: #2e7d32; letter-spacing: 10px;">{otp}</span>
            </div>
            <p style="color: #888; font-size: 13px;">⏰ This code is valid for <strong>{OTP_EXPIRY_MINUTES} minutes</strong>.</p>
            <p style="color: #888; font-size: 13px;">If you did not create a Agri-AI account, please ignore this email.</p>
          </div>
          <div style="padding: 16px; background: #f0faf0; text-align: center;">
            <p style="color: #aaa; font-size: 12px; margin: 0;">© 2026 Agri-AI — AI Crop Diagnosis System</p>
          </div>
        </div>
        """

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = settings.SMTP_FROM
        msg['To'] = to_email

        # Plain text fallback
        plain_text = f"Your Agri-AI OTP is: {otp}\nValid for {OTP_EXPIRY_MINUTES} minutes."
        msg.attach(MIMEText(plain_text, 'plain'))
        msg.attach(MIMEText(body_html, 'html'))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.ehlo()
            server.starttls()   # Upgrade to TLS (required for port 587)
            server.ehlo()
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.sendmail(settings.SMTP_FROM, to_email, msg.as_string())

        print(f"[EmailService] OTP email sent to {to_email} (purpose: {purpose})")
        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"[EmailService] SMTP Authentication failed - check SMTP_USER and SMTP_PASS: {e}")
        return False
    except smtplib.SMTPException as e:
        print(f"[EmailService] SMTP error: {e}")
        return False
    except Exception as e:
        print(f"[EmailService] Unexpected error sending email: {type(e).__name__}: {e}")
        return False


def store_otp(email: str, otp: str, purpose: str) -> None:
    """
    Store OTP in MongoDB `otp_tokens` collection.
    Overwrites any previous OTP for the same email + purpose combination.
    """
    # Delete old OTPs for this email + purpose first
    try:
        db.db['otp_tokens'].delete_many({'email': email, 'purpose': purpose})
    except Exception:
        pass

    # Insert the new OTP
    expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=OTP_EXPIRY_MINUTES)
    db.execute_insert(
        collection='otp_tokens',
        document={
            'email': email.lower().strip(),
            'otp': otp,
            'purpose': purpose,  # 'verify' or 'reset'
            'expires_at': expiry,
            'used': False,
            'created_at': datetime.datetime.utcnow()
        }
    )


def verify_otp(email: str, otp: str, purpose: str) -> dict:
    """
    Verify an OTP for the given email and purpose.
    Returns {'valid': True} or {'valid': False, 'error': 'reason'}.
    """
    results = db.execute_query(
        collection='otp_tokens',
        mongo_query={
            'email': email.lower().strip(),
            'purpose': purpose,
            'used': False
        }
    )

    if not results:
        return {'valid': False, 'error': 'No OTP found. Please request a new one.'}

    # Get the most recent matching OTP
    token = sorted(results, key=lambda x: x.get('created_at', datetime.datetime.min), reverse=True)[0]

    # Check expiry
    if datetime.datetime.utcnow() > token.get('expires_at', datetime.datetime.min):
        return {'valid': False, 'error': 'OTP has expired. Please request a new one.'}

    # Check the actual OTP value
    if token.get('otp') != otp.strip():
        return {'valid': False, 'error': 'Invalid OTP. Please try again.'}

    # Mark as used so it can't be reused
    try:
        db.db['otp_tokens'].update_one(
            {'_id': token['_id']},
            {'$set': {'used': True}}
        )
    except Exception:
        pass

    return {'valid': True}
