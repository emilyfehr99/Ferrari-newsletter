"""
Ferrari F1 Newsletter - Email Sender Module
Sends the newsletter via SMTP
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from typing import List, Optional
import logging
import resend

logger = logging.getLogger(__name__)

WELCOME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Titillium+Web:wght@400;700&display=swap');
    </style>
</head>
<body style="margin: 0; padding: 0; background-color: #1a1a1a; font-family: 'Titillium Web', Arial, sans-serif;">
    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #1a1a1a;">
        <tr>
            <td align="center" style="padding: 40px 10px;">
                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="600" style="background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.3);">
                    <!-- Header Section -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #EF1A2D 0%, #C41422 100%); padding: 0;">
                            <!-- Italian Flag Stripe Top -->
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                <tr>
                                    <td width="33.33%" style="background-color: #00A551; height: 6px;"></td>
                                    <td width="33.33%" style="background-color: #FFFFFF; height: 6px;"></td>
                                    <td width="33.34%" style="background-color: #EF1A2D; height: 6px;"></td>
                                </tr>
                            </table>
                            <!-- Logo & Title -->
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                <tr>
                                    <td align="center" style="padding: 30px 40px 10px 40px;">
                                        <img src="https://1000logos.net/wp-content/uploads/2021/04/Ferrari-logo.png" alt="Ferrari" width="80" style="display: block; margin: 0 auto;">
                                    </td>
                                </tr>
                                <tr>
                                    <td align="center" style="padding: 10px 40px 30px 40px;">
                                        <h1 style="margin: 0; color: #FFF200; font-size: 24px; font-weight: 800; letter-spacing: 2px; text-transform: uppercase;">MARANELLO INSIDER</h1>
                                        <p style="margin: 5px 0 0 0; color: #FFFFFF; font-size: 11px; letter-spacing: 3px; text-transform: uppercase;">Exclusive Technical Briefing</p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px; color: #333333;">
                            <h2 style="color: #EF1A2D; font-size: 20px; margin: 0 0 20px 0;">Benvenuto, Tifoso!</h2>
                            <p style="line-height: 1.6; font-size: 16px; margin: 0 0 20px 0;">You are now officially subscribed to <strong>The Maranello Insider</strong>. You've joined an exclusive group of Ferrari fans who demand more than just headlines.</p>
                            
                            <p style="line-height: 1.6; font-size: 16px; margin: 0 0 15px 0;">Every week, we'll deliver:</p>
                            <ul style="padding-left: 20px; line-height: 1.8; font-size: 15px; margin: 0 0 25px 0;">
                                <li><strong>Technical Deep Dives</strong>: Analysis of SF-26 upgrades and aerodynamic breakthroughs.</li>
                                <li><strong>Insider Briefs</strong>: Direct insights from the paddock and Fiorano testing.</li>
                                <li><strong>Strategic Logic</strong>: Psychological weighting of race narratives and team decisions.</li>
                            </ul>
                            
                            <p style="line-height: 1.6; font-size: 16px; margin: 0 0 0 0;">The next briefing will arrive shortly. Prepare for the most informed F1 experience on the grid.</p>
                            
                            <div style="margin-top: 40px; border-top: 1px solid #eeeeee; padding-top: 20px; text-align: center;">
                                <p style="color: #EF1A2D; font-size: 14px; font-weight: 700; margin: 0;">FORZA FERRARI! 🇮🇹</p>
                            </div>
                        </td>
                    </tr>

                    <!-- Footer Stripe Bottom -->
                    <tr>
                        <td style="padding: 0;">
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                <tr>
                                    <td width="33.33%" style="background-color: #00A551; height: 6px;"></td>
                                    <td width="33.33%" style="background-color: #FFFFFF; height: 6px;"></td>
                                    <td width="33.34%" style="background-color: #EF1A2D; height: 6px;"></td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""


class EmailSender:
    """Sends the newsletter via SMTP"""
    
    def __init__(self, 
                 smtp_server: str = None,
                 smtp_port: int = None,
                 username: str = None,
                 password: str = None):
        """
        Initialize email sender with SMTP credentials.
        Falls back to environment variables if not provided.
        """
        self.smtp_server = smtp_server or os.getenv("SMTP_SERVER", "smtp.gmail.com")
        
        # Handle empty or missing SMTP_PORT
        env_port = os.getenv("SMTP_PORT")
        if smtp_port is not None:
            self.smtp_port = smtp_port
        elif env_port and env_port.strip():
            self.smtp_port = int(env_port)
        else:
            self.smtp_port = 587
            
        self.username = username or os.getenv("SMTP_USERNAME")
        self.password = password or os.getenv("SMTP_PASSWORD")
        
        # Resend Configuration
        self.resend_api_key = os.getenv("RESEND_API_KEY")
        if self.resend_api_key:
            resend.api_key = self.resend_api_key
            logger.info("Resend API key configured. Prioritizing Resend for email dispatch.")
        elif not self.username or not self.password:
            logger.warning("Neither Resend API key nor SMTP credentials are configured. Email sending will fail.")
    
    def send(self, 
             html_content: str,
             recipients: List[str],
             subject: str = "🏎️ Ferrari F1 Weekly Digest",
             from_name: str = "Ferrari F1 Newsletter") -> bool:
        """
        Send the newsletter to a list of recipients.
        Prioritizes Resend if API key is present.
        """
        if self.resend_api_key:
            return self._send_via_resend(html_content, recipients, subject, from_name)
        
        if not self.username or not self.password:
            logger.error("Email configuration missing (no Resend key or SMTP credentials)!")
            return False
            
        return self._send_via_smtp(html_content, recipients, subject, from_name)

    def _send_via_resend(self, html_content: str, recipients: List[str], subject: str, from_name: str) -> bool:
        """Send email using Resend API"""
        try:
            # Resend free tier requirements: 
            # 1. 'From' must be 'onboarding@resend.dev' unless domain is verified
            # 2. Can only send to your own email in test mode
            params = {
                "from": f"{from_name} <onboarding@resend.dev>",
                "to": recipients,
                "subject": subject,
                "html": html_content
            }
            
            response = resend.Emails.send(params)
            logger.info(f"Email sent via Resend successfully to {len(recipients)} recipients")
            return True
        except Exception as e:
            logger.error(f"Resend API error: {e}")
            return False

    def _send_via_smtp(self, html_content: str, recipients: List[str], subject: str, from_name: str) -> bool:
        """Send email using standard SMTP"""
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{from_name} <{self.username}>"
            msg["To"] = ", ".join(recipients)
            
            # Create plain text version (fallback)
            text_content = self._html_to_plaintext(html_content)
            part1 = MIMEText(text_content, "plain")
            part2 = MIMEText(html_content, "html")
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Send via SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.sendmail(self.username, recipients, msg.as_string())
            
            logger.info(f"Email sent via SMTP successfully to {len(recipients)} recipients")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed. Check your credentials.")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email via SMTP: {e}")
            return False
    
    def send_test(self, html_content: str, test_email: str) -> bool:
        """Send a test email to a single recipient"""
        return self.send(
            html_content=html_content,
            recipients=[test_email],
            subject="[TEST] 🏎️ Ferrari F1 Weekly Digest"
        )
    
    def send_confirmation(self, email: str) -> bool:
        """Send a subscription confirmation email"""
        logger.info(f"Sending confirmation email to {email}")
        return self.send(
            html_content=WELCOME_TEMPLATE,
            recipients=[email],
            subject="🏎️ Welcome to the Maranello Insider",
            from_name="Maranello Insider"
        )
    
    def _html_to_plaintext(self, html: str) -> str:
        """Convert HTML to plain text for email fallback"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text(separator='\n', strip=True)
        
        # Clean up whitespace
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return '\n\n'.join(lines)


if __name__ == "__main__":
    # Test configuration check
    sender = EmailSender()
    
    print("Email Sender Configuration Check")
    print("="*40)
    print(f"SMTP Server: {sender.smtp_server}")
    print(f"SMTP Port: {sender.smtp_port}")
    print(f"Username: {'Configured' if sender.username else 'NOT SET'}")
    print(f"Password: {'Configured' if sender.password else 'NOT SET'}")
    print()
    
    if not sender.username or not sender.password:
        print("To configure email, set these environment variables:")
        print("  export SMTP_USERNAME='your-email@gmail.com'")
        print("  export SMTP_PASSWORD='your-app-password'")
        print()
        print("For Gmail, you need to use an App Password:")
        print("  https://myaccount.google.com/apppasswords")
