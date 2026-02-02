"""
Ferrari F1 Newsletter - AI Article Summarizer
Uses Google Gemini API (free tier) or simple extractive summarization as fallback
"""

import requests
import logging
import re
from typing import Optional
from bs4 import BeautifulSoup
# from transformers import pipeline
# import torch
import logging

logger = logging.getLogger(__name__)


def extractive_summarize(text: str, num_sentences: int = 3) -> str:
    """
    Improved extractive summarization that extracts the most relevant sentences.
    Provides richer context than the base implementation and ensures a coherent flow.
    """
    if not text or len(text) < 100:
        return text
    
    # Split into sentences, handling various edge cases
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    
    if len(sentences) <= num_sentences:
        return text
    
    # Selection of key terms for relevance
    key_terms = [
        'ferrari', 'leclerc', 'hamilton', 'f1', 'formula 1',
        'win', 'victory', 'podium', 'race', 'test', 'championship',
        'upgrade', 'development', 'new', 'first', 'announce',
        'performance', 'lap', 'pace', 'car', 'engine', 'team',
        'maranello', 'scuderia', 'vasseur'
    ]
    
    # Scoring for "The Maranello Insider" feel (Psychological Weighting)
    insider_terms = [
        'secret', 'breakthrough', 'innovation', 'advantage', 'legend', 
        'exclusive', 'insight', 'technical', 'development',
        'update', 'optimization', 'efficiency', 'gain', 'data', 'test',
        'shakedown', 'fiorano', 'aerodynamic', 'telemetry'
    ]
    
    scored_sentences = []
    
    for i, sentence in enumerate(sentences):
        score = 0
        sentence_lower = sentence.lower()
        
        # Position scoring (hooks are usually at the beginning or end of paragraphs)
        if i == 0:
            score += 5  # Strong first sentence bonus
        elif i < 3:
            score += 3
            
        # Length scoring (perfect length for a summary sentence: 15-30 words)
        word_count = len(sentence.split())
        if 15 <= word_count <= 30:
            score += 4
        elif 10 <= word_count < 15 or 30 < word_count <= 40:
            score += 2
            
        # Keyword scoring
        for term in key_terms:
            if term in sentence_lower:
                score += 1.5
                
        # Insider (Psychological) scoring
        for term in insider_terms:
            if term in sentence_lower:
                score += 2.5
                
        # Penalty for looking like navigation/junk
        if any(junk in sentence_lower for junk in ['click here', 'subscribe', 'follow us', 'read more']):
            score -= 10
            
        scored_sentences.append((score, i, sentence))
    
    # Sort by score and take top N
    scored_sentences.sort(key=lambda x: x[0], reverse=True)
    top_indices = sorted([x[1] for x in scored_sentences[:num_sentences]])
    
    # Ensure even the extractive result doesn't end mid-sentence if it was already truncated
    result_sentences = []
    for idx in top_indices:
        sent = sentences[idx].strip()
        # If sentence looks truncated or too short, skip it if we have others
        if (sent.endswith('...') or len(sent) < 40) and len(top_indices) > 1:
            continue
        result_sentences.append(sent)
        
    if not result_sentences:
        result_sentences = [sentences[i] for i in top_indices]
        
    result = " ".join(result_sentences)
    
    # Final cleanup of trailing ellipses
    while result.endswith('.') or result.endswith(' '):
        result = result[:-1]
    result += "." # Ensure it ends with a single period
    
    return result


from bs4 import BeautifulSoup
import time

def fetch_article_content(url: str) -> Optional[str]:
    """
    Fetch the main content of an article from its URL.
    Uses Playwright for robust scraping (bypassing 403s/JS requirements).
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.warning("Playwright not installed, falling back to requests")
        return _fetch_with_requests(url)

    logger.info(f"Fetching content via Playwright: {url}")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            # Use a realistic user agent
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            # Go to page
            try:
                page.goto(url, timeout=20000, wait_until="domcontentloaded")
            except Exception as e:
                logger.warning(f"Playwright navigation failed: {e}")
                browser.close()
                return _fetch_with_requests(url)

            # Extract content
            # Try to find common article tags
            content = ""
            selectors = [
                "article", 
                ".article-body", 
                ".post-content", 
                ".entry-content",
                ".story-content",
                "div[class*='content']",
                "div[class*='article']"
            ]
            
            found_content = False
            for selector in selectors:
                try:
                    element = page.query_selector(selector)
                    if element:
                        # Get paragraphs
                        paragraphs = element.query_selector_all("p")
                        if len(paragraphs) > 2:
                            text_parts = []
                            for p_elem in paragraphs:
                                txt = p_elem.inner_text().strip()
                                if len(txt) > 60: # Filter short junk
                                    text_parts.append(txt)
                            
                            if text_parts:
                                content = " ".join(text_parts)
                                found_content = True
                                break
                except:
                    continue
            
            # Fallback: get all P tags if structure extract failed
            if not content:
                paragraphs = page.query_selector_all("p")
                text_parts = [
                    p.inner_text().strip() 
                    for p in paragraphs 
                    if len(p.inner_text().strip()) > 60
                ]
                content = " ".join(text_parts)

            browser.close()
            
            if content and len(content) > 500:
                logger.info(f"✅ Successfully fetched {len(content)} chars via Playwright")
                return content
            else:
                logger.warning("Playwright fetched insufficient content, trying requests fallback")
                return _fetch_with_requests(url)

    except Exception as e:
        logger.error(f"Playwright fetch error: {e}")
        return _fetch_with_requests(url)

def _fetch_with_requests(url: str) -> Optional[str]:
    """Fallback fetching using requests"""
    if not url:
        return None
        
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }
    
    try:
        # Respect generic rate limits
        time.sleep(0.5)
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            logger.warning(f"Failed to fetch article: {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove unwanted elements
        for script in soup(["script", "style", "nav", "header", "footer", "iframe", "aside", "div.sidebar", "div.related"]):
            script.decompose()
            
        # Try to find the main article container first
        article_body = soup.find('article')
        if not article_body:
            # Common class names for article content
            article_body = soup.find('div', class_=re.compile(r'(content|article-body|post-content|entry-content)', re.I))
            
        # Use the article body if found, otherwise use the whole soup
        context = article_body if article_body else soup
            
        # Extract text from paragraphs within the context
        paragraphs = context.find_all('p')
        
        # Filter out short/navigational paragraphs
        content_paragraphs = [p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 60]
        
        if not content_paragraphs:
            # Fallback to broader search if strict filtering failed
            content_paragraphs = [p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 30]
            
        if not content_paragraphs:
            return None
            
        return " ".join(content_paragraphs)
        
    except Exception as e:
        logger.error(f"Error fetching article content: {e}")
        return None


# ... (keep existing imports)
# Remove top-level transformers imports
# from transformers import pipeline
# import torch
import logging

logger = logging.getLogger(__name__)

class LocalSummarizer:
    _instance = None
    _summarizer = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        # Check for disable flag (useful for testing or avoiding crashes on some systems)
        if os.getenv("DISABLE_LOCAL_AI"):
            logger.info("🚫 Local AI Summarizer disabled via environment variable")
            self._summarizer = None
            return

        try:
            from transformers import pipeline
            import torch
        except ImportError:
            logger.error("Transformers/Torch not installed")
            self._summarizer = None
            return

        self.device = 0 if torch.cuda.is_available() else -1
        if torch.backends.mps.is_available():
             self.device = "mps" # Use Metal on Mac if available
        
        logger.info(f"Initializing Local AI Summarizer on device: {self.device}...")
        try:
            # Use distilbart-cnn-12-6 for a good balance of speed and quality
            self._summarizer = pipeline(
                "summarization", 
                model="sshleifer/distilbart-cnn-12-6", 
                device=self.device
            )
            logger.info("✅ Local AI model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load local AI model: {e}")
            self._summarizer = None

    def summarize(self, text: str, max_length: int = 150, min_length: int = 50) -> Optional[str]:
        if not self._summarizer:
            return None
            
        try:
            # Truncate input to model's limit (usually 1024 tokens)
            # A rough char limit is safer to avoid tokenization overhead here
            if len(text) > 4000:
                text = text[:4000]
                
            summary = self._summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
            if summary and len(summary) > 0:
                return summary[0]['summary_text']
        except Exception as e:
            logger.warning(f"AI summarization error: {e}")
            return None

def summarize_article(title: str, summary: str, full_text: str = None, url: str = None) -> str:
    """
    Summarize an article using Local AI (Generative) or Extractive fallback.
    """
    # Try to fetch full text if not provided and we have a URL
    if not full_text and url:
        logger.info(f"Fetching full text for summarization: {title[:30]}...")
        full_text = fetch_article_content(url)
    
    text_to_summarize = full_text if full_text else summary
    
    # Validation
    if not text_to_summarize or len(text_to_summarize) < 200:
        return summary
    
    # 1. Try AI Summarization
    try:
        ai_agent = LocalSummarizer.get_instance()
        ai_summary = ai_agent.summarize(text_to_summarize)
        if ai_summary:
            return ai_summary
    except Exception as e:
        logger.debug(f"AI summarization skipped/failed: {e}")

    # 2. Fallback to Extractive with adaptive sentence count
    logger.info("Falling back to polished extractive summarization")
    
    # For featured/short articles use 3 sentences, for technical more context might be needed
    target_sentences = 2 if len(text_to_summarize) < 1000 else 3
    result = extractive_summarize(text_to_summarize, num_sentences=target_sentences)
    
    # Clean up any anti-bot messages that might have leaked through
    result = clean_bot_messages(result)
    
    # Ensure it's not too long for the newsletter
    if len(result) > 600:
        # One last attempt to shorten if it's still massive
        result = extractive_summarize(result, num_sentences=2)
        
    return result

def clean_bot_messages(text: str) -> str:
    """Detect and remove common anti-bot/protection messages from scraped text"""
    if not text:
        return text
        
    bot_keywords = [
        "Anubis is a compromise",
        "administrator of this website has set up Anubis",
        "protect the server against the scourge of AI companies",
        "aggressively scraping websites"
    ]
    
    for kw in bot_keywords:
        if kw in text:
            # If the summary is mostly bot message, return a placeholder
            if len(text) < 500:
                logger.warning(f"Detected anti-bot message dominating summary, reducing text.")
                return "Social media content currently unavailable due to source site protection."
            # Otherwise just strip the first paragraph if it contains the keyword
            paragraphs = text.split('\n\n')
            clean_paragraphs = [p for p in paragraphs if not any(kw in p for kw in bot_keywords)]
            return '\n\n'.join(clean_paragraphs)
            
    return text


if __name__ == "__main__":
    # Test the summarizer
    logging.basicConfig(level=logging.INFO)
    
    test_text = """
    Lewis Hamilton finished the first pre-season test at Barcelona with the quickest time of the week, 
    sending out a strong signal in his debut for Ferrari. The seven-time world champion completed 127 laps 
    on the final day of running, focusing on long-run pace before unleashing a performance run late in the session. 
    Hamilton's 1:18.567 was three tenths faster than Max Verstappen's best effort for Red Bull, though conditions 
    and fuel loads make direct comparisons difficult. Team-mate Charles Leclerc finished fourth overall, 
    praising the collaborative atmosphere within the Italian team. Ferrari appears to have made significant 
    progress with their SF-26 car, particularly in high-speed corners where the team struggled last season.
    """
    
    print("Testing Extractive Summarizer...")
    print("-" * 50)
    
    result = summarize_article("Hamilton tops Barcelona test", test_text)
    
    print(f"Original length: {len(test_text)} chars")
    print(f"Summary length: {len(result)} chars")
    print(f"\n✅ Summary:\n{result}")
