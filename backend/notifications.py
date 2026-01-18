import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config


def send_booking_email(client_email, client_name, booking_type, date, time, meet_link):
    """Sends a professional confirmation email to the client."""
    if not config.SMTP_EMAIL or "@gmail.com" in config.SMTP_EMAIL and "password" in config.SMTP_PASSWORD:
        print(f"  [EMAIL] Skipped: SMTP credentials not configured.")
        return False

    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = config.SMTP_EMAIL
        msg['To'] = client_email
        msg['Subject'] = config.EMAIL_SUBJECT

        # SELECT TEMPLATE & LINK DISPLAY
        is_tour = "tour" in booking_type.lower()
        
        if is_tour:
            body = config.EMAIL_TEMPLATE_TOUR_HTML.format(
                name=client_name,
                date=date,
                time=time
            )
        else:
            # Standard Meeting Template Logic
            if meet_link:
                meet_display = f'''
                <div style="text-align: center; margin-bottom: 32px;">
                    <a href="{meet_link}" style="display: inline-block; padding: 16px 32px; background-color: #7c3aed; color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 6px -1px rgba(124, 58, 237, 0.2);">
                        Join Meeting
                    </a>
                    <p style="margin-top: 12px; font-size: 13px; color: #6b7280;">Meeting Link: {meet_link}</p>
                </div>
                '''
            else:
                meet_display = '<p style="color: #6b7280; text-align: center; margin-bottom: 32px;">Note: Meeting link will be shared by the manager shortly.</p>'

            body = config.EMAIL_TEMPLATE_HTML.format(
                name=client_name,
                booking_type=booking_type,
                date=date,
                time=time,
                meet_display=meet_display
            )
        
        msg.attach(MIMEText(body, 'html'))

        # Send email
        with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
            server.starttls()
            server.login(config.SMTP_EMAIL, config.SMTP_PASSWORD)
            server.send_message(msg)
            
        print(f"  [EMAIL] Success: Sent confirmation to {client_email}")
        return True
    except Exception as e:
        print(f"  [EMAIL] Failed: {e}")
        return False
