"""
Ferrari F1 Newsletter - Main Orchestrator
Combines all modules to generate and send the weekly newsletter
"""

import os
import sys
import argparse
from datetime import datetime
import logging

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from news_scraper import FerrariNewsScraper
from content_filter import ContentFilter
from template_renderer import TemplateRenderer
from email_sender import EmailSender
from subscriber_manager import SubscriberManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NewsletterGenerator:
    """Main orchestrator for the Ferrari F1 Newsletter"""
    
    def __init__(self, days_back: int = 7):
        self.scraper = FerrariNewsScraper(days_back=days_back)
        self.filter = ContentFilter(self.scraper)
        self.renderer = TemplateRenderer()
        self.sender = EmailSender()
        self.subscribers = SubscriberManager()
    
    def generate(self, save_preview: bool = True) -> str:
        """
        Generate the newsletter HTML.
        
        Args:
            save_preview: If True, save a preview HTML file
            
        Returns:
            The rendered HTML newsletter
        """
        logger.info("🏎️ Starting Ferrari F1 Newsletter generation...")
        
        # Step 1: Scrape news from all sources
        logger.info("📰 Scraping news from sources...")
        articles = self.scraper.scrape_all()
        logger.info(f"   Found {len(articles)} total articles")
        
        # Step 2: Filter and select content
        logger.info("🔍 Filtering for Ferrari content...")
        selected = self.filter.process_articles(articles)
        logger.info(f"   Selected: {len(selected['featured'])} featured, "
                   f"{len(selected['headlines'])} headlines, "
                   f"{len(selected['technical'])} technical")
        
        # Step 3: Render the template
        logger.info("🎨 Rendering newsletter template...")
        html = self.renderer.render(selected)
        
        # Step 4: Save preview if requested
        if save_preview:
            preview_path = os.path.join(
                os.path.dirname(__file__), 
                "..", 
                "index.html"
            )
            with open(preview_path, "w") as f:
                f.write(html)
            logger.info(f"   Preview saved to: {preview_path}")
        
        logger.info("✅ Newsletter generated successfully!")
        return html
    
    def send(self, recipients: list, html: str = None) -> bool:
        """
        Send the newsletter to recipients.
        
        Args:
            recipients: List of email addresses
            html: Pre-generated HTML (generates fresh if not provided)
            
        Returns:
            True if sent successfully
        """
        if html is None:
            html = self.generate(save_preview=False)
        
        logger.info(f"📧 Sending newsletter to {len(recipients)} recipients...")
        success = self.sender.send(html, recipients)
        
        if success:
            logger.info("✅ Newsletter sent successfully!")
        else:
            logger.error("❌ Failed to send newsletter")
        
        return success
    
    def preview(self) -> str:
        """Generate newsletter and return path to preview file"""
        html = self.generate(save_preview=True)
        preview_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "index.html")
        )
        return preview_path

    def send_to_all_subscribers(self, html: str = None) -> bool:
        """Send newsletter to all active subscribers"""
        subscribers = self.subscribers.get_active_subscribers()
        emails = [s['email'] for s in subscribers]
        
        if not emails:
            logger.warning("No active subscribers found.")
            return False
            
        return self.send(emails, html)

    def subscribe_user(self, email: str) -> bool:
        """Subscribe a new user and send confirmation email"""
        logger.info(f"Subscribing user: {email}")
        result = self.subscribers.subscribe(email)
        
        if result.get("success"):
            logger.info(f"User {email} added to database. Sending confirmation...")
            self.sender.send_confirmation(email)
            return True
        else:
            logger.error(f"Failed to subscribe user {email}: {result.get('error')}")
            return False


def main():
    """Command line interface for the newsletter generator"""
    parser = argparse.ArgumentParser(
        description="Ferrari F1 Weekly Newsletter Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Generate a preview:
    python main.py --preview
    
  Send to a test email:
    python main.py --test-email your@email.com
    
  Send to multiple recipients:
    python main.py --send email1@test.com email2@test.com
    
  Send to all subscribers:
    python main.py --send-all

  Scrape from last 3 days only:
    python main.py --preview --days 3
        """
    )
    
    parser.add_argument(
        "--preview", 
        action="store_true",
        help="Generate a preview HTML file"
    )
    
    parser.add_argument(
        "--test-email",
        type=str,
        metavar="EMAIL",
        help="Send a test email to this address"
    )
    
    parser.add_argument(
        "--send",
        nargs="+",
        metavar="EMAIL",
        help="Send newsletter to these email addresses"
    )
    
    parser.add_argument(
        "--send-all",
        action="store_true",
        help="Send newsletter to ALL active subscribers"
    )

    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to look back for news (default: 7)"
    )

    parser.add_argument(
        "--subscribe",
        type=str,
        metavar="EMAIL",
        help="Subscribe a new email address and send confirmation"
    )
    
    args = parser.parse_args()
    
    # Create generator
    generator = NewsletterGenerator(days_back=args.days)
    
    if args.send:
        # Send to specified recipients
        html = generator.generate(save_preview=False)
        generator.send(args.send, html)
    elif args.send_all:
        # Send to all subscribers
        html = generator.generate(save_preview=False)
        generator.send_to_all_subscribers(html)
    elif args.test_email:
        # Send test email
        html = generator.generate(save_preview=False)
        generator.send([args.test_email], html)
    elif args.subscribe:
        # Subscribe new user
        generator.subscribe_user(args.subscribe)
    else:
        # Default action: generate preview
        preview_path = generator.preview()
        print(f"\n🏎️ Ferrari F1 Newsletter Preview Generated!")
        print(f"   Open in browser: file://{preview_path}")
        print()


if __name__ == "__main__":
    main()

