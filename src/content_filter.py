"""
Ferrari F1 Newsletter - Content Filter Module
Filters and processes scraped articles for the newsletter
"""

from typing import List, Tuple
from difflib import SequenceMatcher
from news_scraper import Article, FerrariNewsScraper
import logging

try:
    from summarizer import summarize_article
    SUMMARIZER_AVAILABLE = True
except ImportError:
    SUMMARIZER_AVAILABLE = False

logger = logging.getLogger(__name__)


class ContentFilter:
    """Filters and categorizes Ferrari F1 content"""
    
    # Priority keywords - articles with these get boosted
    PRIORITY_KEYWORDS = [
        "exclusive", "breaking", "official", "confirmed", "announced",
        "upgrade", "new", "first", "test", "unveil", "reveal"
    ]
    
    # Categories with their associated keywords
    CATEGORY_KEYWORDS = {
        "Race Weekend": [
            "race", "grand prix", "gp", "qualifying", "quali", "sprint",
            "podium", "win", "victory", "finish", "result", "grid"
        ],
        "Technical": [
            "downforce", "aerodynamic", "aero", "power unit", "engine",
            "suspension", "floor", "diffuser", "sidepod", "wing",
            "brake", "upgrade", "development", "chassis", "gearbox",
            "mgu", "ers", "battery", "cooling", "exhaust"
        ],
        "Driver News": [
            "leclerc", "hamilton", "driver", "interview", "contract",
            "comment", "said", "says", "believes", "thinks", "feeling"
        ],
        "Strategy": [
            "strategy", "prediction", "analysis", "expect", "outlook",
            "forecast", "preview", "review", "comparison"
        ]
    }
    
    def __init__(self, scraper: FerrariNewsScraper = None):
        self.scraper = scraper or FerrariNewsScraper()
    
    def filter_ferrari_content(self, articles: List[Article]) -> List[Article]:
        """Filter articles to only include Ferrari-related content"""
        ferrari_articles = []
        
        for article in articles:
            if self.scraper.is_ferrari_related(article):
                # Categorize the article
                article.category = self._categorize(article)
                ferrari_articles.append(article)
        
        logger.info(f"Filtered {len(ferrari_articles)} Ferrari articles from {len(articles)} total")
        return ferrari_articles
    
    def deduplicate(self, articles: List[Article], 
                    title_threshold: float = 0.6,
                    summary_threshold: float = 0.5) -> List[Article]:
        """Remove duplicate or very similar articles based on title AND summary"""
        if not articles:
            return []
        
        unique_articles = []
        
        for article in articles:
            is_duplicate = False
            
            for existing in unique_articles:
                # Check title similarity
                title_sim = self._calculate_similarity(article.title, existing.title)
                # Check summary similarity (first 200 chars)
                summary_sim = self._calculate_similarity(
                    article.summary[:200] if article.summary else "",
                    existing.summary[:200] if existing.summary else ""
                )
                
                # If either title is very similar OR summary is very similar, it's a dupe
                if title_sim > title_threshold or (summary_sim > summary_threshold and title_sim > 0.4):
                    is_duplicate = True
                    # Keep the one from more authoritative source
                    if self._get_source_priority(article.source) > self._get_source_priority(existing.source):
                        unique_articles.remove(existing)
                        unique_articles.append(article)
                    break
            
            if not is_duplicate:
                unique_articles.append(article)
        
        logger.info(f"Deduplicated to {len(unique_articles)} unique articles")
        return unique_articles
    
    def prioritize(self, articles: List[Article]) -> List[Article]:
        """Sort articles by relevance and priority"""
        
        def priority_score(article: Article) -> Tuple[int, int, float]:
            """Calculate priority score for sorting"""
            # Category priority (Technical > Race Weekend > Driver News > Strategy > General)
            category_scores = {
                "Technical": 5,
                "Race Weekend": 4,
                "Driver News": 3,
                "Strategy": 2,
                "General": 1
            }
            cat_score = category_scores.get(article.category, 0)
            
            # Priority keyword boost
            text = f"{article.title} {article.summary}".lower()
            keyword_score = sum(1 for kw in self.PRIORITY_KEYWORDS if kw in text)
            
            # Recency score (timestamp as float for ordering)
            recency_score = article.published_date.timestamp()
            
            return (cat_score, keyword_score, recency_score)
        
        sorted_articles = sorted(articles, key=priority_score, reverse=True)
        return sorted_articles
    
    def select_top_articles(self, articles: List[Article], 
                            max_featured: int = 1,
                            max_regular: int = 6,
                            max_technical: int = 5) -> dict:
        """Select top articles for each section of the newsletter"""
        
        featured = []
        regular = []
        technical = []
        
        for article in articles:
            if article.category == "Technical" and len(technical) < max_technical:
                technical.append(article)
            elif len(featured) < max_featured:
                featured.append(article)
            elif len(regular) < max_regular:
                regular.append(article)
        
        return {
            "featured": featured,
            "headlines": regular,
            "technical": technical
        }
    
    def _categorize(self, article: Article) -> str:
        """Categorize an article based on keywords"""
        text = f"{article.title} {article.summary}".lower()
        
        # Count keyword matches for each category
        category_scores = {}
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            return max(category_scores, key=category_scores.get)
        return "General"
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two strings"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def _get_source_priority(self, source: str) -> int:
        """Get priority ranking for a news source"""
        priorities = {
            "Ferrari.com": 5,
            "F1 Official": 4,
            "Motorsport.com": 3,
            "The Race": 3,
            "Autosport": 2,
        }
        return priorities.get(source, 1)
    
    def process_articles(self, articles: List[Article]) -> dict:
        """Full processing pipeline: filter, dedupe, prioritize, select, summarize"""
        # Filter for Ferrari content
        ferrari_articles = self.filter_ferrari_content(articles)
        
        # Remove duplicates
        unique_articles = self.deduplicate(ferrari_articles)
        
        # Prioritize
        prioritized = self.prioritize(unique_articles)
        
        # Select top articles for newsletter
        selected = self.select_top_articles(prioritized)
        
        # Apply AI summarization if available
        if SUMMARIZER_AVAILABLE:
            logger.info("🤖 Applying AI summarization...")
            selected = self._summarize_articles(selected)
        
        return selected
    
    def _summarize_articles(self, selected: dict) -> dict:
        """Apply AI summarization to selected articles"""
        for category, articles in selected.items():
            for article in articles:
                try:
                    # Pass URL to allow fetching full content
                    ai_summary = summarize_article(article.title, article.summary, url=article.url)
                    if ai_summary and ai_summary != article.summary:
                        article.summary = ai_summary
                        logger.info(f"✅ Summarized: {article.title[:50]}...")
                except Exception as e:
                    logger.warning(f"Summarization failed for {article.title[:30]}: {e}")
        return selected


if __name__ == "__main__":
    # Test the filter
    from news_scraper import FerrariNewsScraper
    
    scraper = FerrariNewsScraper(days_back=7)
    articles = scraper.scrape_all()
    
    filter = ContentFilter(scraper)
    selected = filter.process_articles(articles)
    
    print("\n" + "="*60)
    print("NEWSLETTER CONTENT SELECTION")
    print("="*60)
    
    print("\n📰 FEATURED ARTICLE:")
    for article in selected["featured"]:
        print(f"  • {article.title}")
        print(f"    Source: {article.source}")
    
    print("\n📋 HEADLINES:")
    for article in selected["headlines"]:
        print(f"  • [{article.category}] {article.title}")
    
    print("\n⚙️ TECHNICAL:")
    for article in selected["technical"]:
        print(f"  • {article.title}")
