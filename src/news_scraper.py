"""
Ferrari F1 Newsletter - News Scraper Module
Scrapes Ferrari F1 news from multiple sources
"""

import feedparser
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Article:
    """Represents a single news article"""
    title: str
    summary: str
    source: str
    url: str
    published_date: datetime
    category: str = "General"
    image_url: Optional[str] = None
    
    def __hash__(self):
        return hash(self.title.lower())
    
    def __eq__(self, other):
        if not isinstance(other, Article):
            return False
        return self.title.lower() == other.title.lower()


class FerrariNewsScraper:
    """Scrapes Ferrari F1 news from multiple sources"""
    
    # RSS Feed URLs
    RSS_FEEDS = {
        "F1 Official": "https://www.formula1.com/content/fom-website/en/latest/all.xml",
        "Motorsport.com": "https://www.motorsport.com/rss/f1/news/",
        "The Race": "https://the-race.com/feed/",
        "Autosport": "https://www.autosport.com/rss/f1/news/",
        "MotorsportWeek": "https://www.motorsportweek.com/feed/",
    }
    
    # X/Twitter profiles to scrape (via Nitter for better reliability)
    TWITTER_PROFILES = [
        "formularacers_",   # Formula Racers - F1 news
        "GazzettaFerrari",  # Italian Ferrari-focused news
    ]
    
    # Keywords to identify Ferrari-related content
    FERRARI_KEYWORDS = [
        "ferrari", "leclerc", "hamilton", "lewis hamilton", "charles leclerc",
        "sf-26", "sf26", "maranello", "scuderia", "vasseur", "fred vasseur",
        "prancing horse", "tifosi", "italian team"
    ]
    
    # Technical keywords for filtering
    TECHNICAL_KEYWORDS = [
        "downforce", "aerodynamic", "aero", "power unit", "engine", "pu",
        "suspension", "floor", "diffuser", "sidepod", "front wing", "rear wing",
        "brake", "tire", "tyre", "compound", "strategy", "pit stop", "drs",
        "upgrade", "development", "wind tunnel", "cfd", "simulation",
        "chassis", "gearbox", "mgu-k", "mgu-h", "ers", "battery"
    ]
    
    def __init__(self, days_back: int = 7, min_year: int = 2026):
        self.days_back = days_back
        self.min_year = min_year  # Only include articles from this year onwards
        self.cutoff_date = datetime.now() - timedelta(days=days_back)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
    
    def scrape_all(self) -> List[Article]:
        """Scrape all sources and return combined articles"""
        articles = []
        
        # Scrape RSS feeds
        for source_name, feed_url in self.RSS_FEEDS.items():
            try:
                feed_articles = self._scrape_rss_feed(feed_url, source_name)
                articles.extend(feed_articles)
                logger.info(f"Scraped {len(feed_articles)} articles from {source_name}")
            except Exception as e:
                logger.error(f"Error scraping {source_name}: {e}")
        
        # Scrape Ferrari official news
        try:
            ferrari_articles = self._scrape_ferrari_official()
            articles.extend(ferrari_articles)
            logger.info(f"Scraped {len(ferrari_articles)} articles from Ferrari.com")
        except Exception as e:
            logger.error(f"Error scraping Ferrari.com: {e}")
            
        # Scrape Twitter/X profiles via Nitter
        try:
            tweet_articles = self._scrape_twitter_profiles()
            articles.extend(tweet_articles)
            logger.info(f"Scraped {len(tweet_articles)} tweets from X/Twitter")
        except Exception as e:
            logger.error(f"Error scraping Twitter: {e}")
        
        # Remove duplicates
        unique_articles = list(set(articles))
        
        # Sort by date (newest first)
        unique_articles.sort(key=lambda x: x.published_date, reverse=True)
        
        return unique_articles

    def _scrape_twitter_profiles(self) -> List[Article]:
        """Scrape Twitter profiles using Playwright via Nitter with randomized instance selection"""
        articles = []
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            logger.error("Playwright not installed. Cannot scrape Twitter.")
            return []

        import random
        # List of Nitter instances to try
        nitter_instances = [
            "https://nitter.net",
            "https://nitter.cz",
            "https://nitter.privacydev.net",
            "https://nitter.poast.org",
            "https://nitter.lucabased.xyz",
            "https://nitter.moomoo.me"
        ]
        random.shuffle(nitter_instances)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            
            for profile in self.TWITTER_PROFILES:
                profile_success = False
                
                # Try at most 3 instances per profile to avoid excessive time
                for instance in nitter_instances[:3]:
                    if profile_success:
                        break
                        
                    context = browser.new_context(
                        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                    )
                    page = context.new_page()
                    
                    try:
                        url = f"{instance}/{profile}"
                        logger.info(f"Scraping {profile} via {instance}...")
                        
                        # Go to page and wait for timeline
                        page.goto(url, timeout=12000, wait_until="domcontentloaded")
                        
                        # Wait for timeline items
                        try:
                            page.wait_for_selector(".timeline-item", timeout=5000)
                        except:
                            context.close()
                            continue
                            
                        # Extract tweets
                        tweets = page.query_selector_all(".timeline-item")
                        count = 0
                        
                        # Get current date for tweets that don't have clear ones
                        pub_date = datetime.now()
                        
                        for tweet in tweets[:8]: # Check latest 8 tweets
                            try:
                                content_div = tweet.query_selector(".tweet-content")
                                if not content_div:
                                    continue
                                    
                                text = content_div.inner_text().strip()
                                
                                # Detect and skip anti-bot messages
                                if "Anubis" in text or "AI companies aggressively scraping" in text:
                                    continue
                                    
                                # Check filtering for Ferrari keywords
                                if not any(k in text.lower() for k in self.FERRARI_KEYWORDS):
                                    continue

                                # Filter low-value short tweets
                                if len(text) < 100:
                                    continue
                                
                                # Generate a better title from the text (avoid mid-word truncation)
                                clean_text = re.sub(r'[^\w\s\.,!?\-\'\"]', '', text).strip()
                                if len(clean_text) > 80:
                                    # Find last space before 80
                                    last_space = clean_text[:80].rfind(' ')
                                    title = clean_text[:last_space].strip() + "..." if last_space > 0 else clean_text[:80] + "..."
                                else:
                                    title = clean_text
                                
                                # Create article
                                article = Article(
                                    title=title,
                                    summary=text,
                                    source=f"X (@{profile})",
                                    url=url,
                                    published_date=pub_date,
                                    category="Social Media"
                                )
                                articles.append(article)
                                count += 1
                                if count >= 3: # Max 3 tweets per profile
                                    break
                            except Exception:
                                continue
                        
                        if count > 0:
                            profile_success = True
                            logger.info(f"Found {count} tweets for {profile}")
                        
                    except Exception as e:
                        logger.debug(f"Error scraping {instance}: {e}")
                    finally:
                        context.close()
                
                if not profile_success:
                    logger.warning(f"Failed to scrape tweets for {profile} after trying multiple instances")
            
            browser.close()
            
        return articles

    def _scrape_rss_feed(self, feed_url: str, source_name: str) -> List[Article]:
        """Scrape articles from an RSS feed"""
        articles = []
        
        try:
            # Use requests to get content first
            response = requests.get(feed_url, headers=self.headers, timeout=15, allow_redirects=True)
            response.raise_for_status()
            content = response.content
            
            feed = feedparser.parse(content)
            
            for entry in feed.entries[:50]:
                pub_date = self._parse_date(entry)
                
                if pub_date and pub_date < self.cutoff_date:
                    continue
                
                if pub_date and pub_date.year < self.min_year:
                    continue
                
                summary = ""
                if hasattr(entry, 'summary'):
                    summary = self._clean_html(entry.summary)
                elif hasattr(entry, 'description'):
                    summary = self._clean_html(entry.description)
                
                image_url = None
                if hasattr(entry, 'media_content') and entry.media_content:
                    image_url = entry.media_content[0].get('url')
                elif hasattr(entry, 'enclosures') and entry.enclosures:
                    image_url = entry.enclosures[0].get('href')
                
                article = Article(
                    title=entry.title,
                    summary=summary if summary else "", # No character limit here, handled by summarizer
                    source=source_name,
                    url=entry.link,
                    published_date=pub_date or datetime.now(),
                    image_url=image_url
                )
                
                articles.append(article)
                
        except Exception as e:
            logger.error(f"Error parsing RSS feed {feed_url}: {e}")
        
        return articles

    def _scrape_ferrari_official(self) -> List[Article]:
        """Scrape official Ferrari news using Playwright to handle shadow DOM."""
        url = "https://www.ferrari.com/en-EN/formula1/news"
        articles = []
        
        logger.info(f"Scraping Ferrari official news via Playwright: {url}...")
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
                
                page.goto(url, timeout=30000, wait_until="networkidle")
                # Wait for the specific element to be present (Playwright pierces shadow DOM)
                page.wait_for_selector(".f-card-main", timeout=10000)
                
                cards = page.query_selector_all(".f-card-main")
                
                for card in cards[:10]:
                    try:
                        link_elem = card.query_selector("a.f-card-main__link")
                        if not link_elem:
                            continue
                            
                        title_elem = card.query_selector(".f-card-main__title")
                        title = title_elem.inner_text().strip() if title_elem else link_elem.inner_text().strip()
                        article_url = link_elem.get_attribute("href")
                        
                        if article_url and not article_url.startswith('http'):
                            article_url = f"https://www.ferrari.com{article_url}"
                            
                        desc_elem = card.query_selector(".f-card-main__description")
                        summary = desc_elem.inner_text().strip() if desc_elem else ""
                        
                        if title and article_url:
                            article = Article(
                                title=title,
                                summary=summary if summary else "Official news from Maranello.", # Context for summarizer
                                source="Ferrari.com",
                                url=article_url,
                                published_date=datetime.now(),
                                category="Official"
                            )
                            articles.append(article)
                    except Exception as e:
                        logger.debug(f"Error parsing Ferrari card: {str(e)}")
                        continue
                        
                browser.close()
        except Exception as e:
            logger.error(f"Error scraping Ferrari.com with Playwright: {str(e)}")
            
        return articles

    def _parse_date(self, entry) -> Optional[datetime]:
        """Parse date from RSS entry"""
        date_fields = ['published_parsed', 'updated_parsed', 'created_parsed']
        
        for field in date_fields:
            if hasattr(entry, field) and getattr(entry, field):
                try:
                    time_struct = getattr(entry, field)
                    return datetime(*time_struct[:6])
                except:
                    pass
        
        # Try parsing from string
        date_strings = ['published', 'updated', 'created']
        for field in date_strings:
            if hasattr(entry, field):
                try:
                    from dateutil import parser
                    return parser.parse(getattr(entry, field))
                except:
                    pass
        
        return None
    
    def _clean_html(self, html_text: str) -> str:
        """Remove HTML tags from text"""
        if not html_text:
            return ""
        soup = BeautifulSoup(html_text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def is_ferrari_related(self, article: Article) -> bool:
        """Check if an article is related to Ferrari"""
        text = f"{article.title} {article.summary}".lower()
        return any(keyword in text for keyword in self.FERRARI_KEYWORDS)
    
    def is_technical(self, article: Article) -> bool:
        """Check if an article has technical content"""
        text = f"{article.title} {article.summary}".lower()
        return any(keyword in text for keyword in self.TECHNICAL_KEYWORDS)
    
    def categorize(self, article: Article) -> str:
        """Categorize an article"""
        text = f"{article.title} {article.summary}".lower()
        
        if any(kw in text for kw in ["race", "grand prix", "gp", "quali", "sprint"]):
            return "Race Weekend"
        elif self.is_technical(article):
            return "Technical"
        elif any(kw in text for kw in ["leclerc", "hamilton", "driver", "contract", "interview"]):
            return "Driver News"
        elif any(kw in text for kw in ["strategy", "prediction", "analysis"]):
            return "Strategy"
        else:
            return "General"


if __name__ == "__main__":
    # Test the scraper
    scraper = FerrariNewsScraper(days_back=7)
    articles = scraper.scrape_all()
    
    # Filter for Ferrari-related articles
    ferrari_articles = [a for a in articles if scraper.is_ferrari_related(a)]
    
    print(f"\n{'='*60}")
    print(f"Found {len(articles)} total articles")
    print(f"Found {len(ferrari_articles)} Ferrari-related articles")
    print(f"{'='*60}\n")
    
    for article in ferrari_articles[:10]:
        article.category = scraper.categorize(article)
        print(f"[{article.category}] {article.title}")
        print(f"  Source: {article.source} | Date: {article.published_date.strftime('%Y-%m-%d')}")
        print(f"  Summary: {article.summary[:150]}...")
        print()
