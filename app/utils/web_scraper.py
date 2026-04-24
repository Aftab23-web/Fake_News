"""
Web Scraper for extracting article content from URLs
Uses BeautifulSoup to scrape news article text
"""

import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urlparse
import time

# Configure logging
logger = logging.getLogger(__name__)


class WebScraper:
    """Class for scraping news articles from URLs"""
    
    def __init__(self, timeout=10):
        """
        Initialize web scraper
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def is_valid_url(self, url):
        """
        Validate URL format
        
        Args:
            url: URL string to validate
            
        Returns:
            Boolean indicating if URL is valid
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def scrape_article(self, url):
        """
        Scrape article content from URL
        
        Args:
            url: URL of the news article
            
        Returns:
            Dictionary with scraped content and metadata
        """
        result = {
            'success': False,
            'url': url,
            'title': '',
            'text': '',
            'author': '',
            'publish_date': '',
            'error': None
        }
        
        # Validate URL
        if not self.is_valid_url(url):
            result['error'] = 'Invalid URL format'
            logger.error(f"❌ Invalid URL: {url}")
            return result
        
        try:
            logger.info(f"🔍 Scraping URL: {url}")
            
            # Send GET request
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = self._extract_title(soup)
            result['title'] = title
            
            # Extract article text
            text = self._extract_text(soup)
            result['text'] = text
            
            # Extract metadata
            result['author'] = self._extract_author(soup)
            result['publish_date'] = self._extract_date(soup)
            
            # Check if we got meaningful content
            if len(text) < 100:
                result['error'] = 'Insufficient content extracted (less than 100 characters)'
                logger.warning(f"⚠️  Insufficient content from: {url}")
            else:
                result['success'] = True
                logger.info(f"✅ Successfully scraped: {url}")
            
            return result
            
        except requests.exceptions.Timeout:
            result['error'] = 'Request timeout - server took too long to respond'
            logger.error(f"❌ Timeout scraping: {url}")
            
        except requests.exceptions.ConnectionError:
            result['error'] = 'Connection error - could not reach the server'
            logger.error(f"❌ Connection error: {url}")
            
        except requests.exceptions.HTTPError as e:
            result['error'] = f'HTTP error: {e.response.status_code}'
            logger.error(f"❌ HTTP error for {url}: {e}")
            
        except Exception as e:
            result['error'] = f'Unexpected error: {str(e)}'
            logger.error(f"❌ Error scraping {url}: {e}")
        
        return result
    
    def _extract_title(self, soup):
        """Extract article title from parsed HTML"""
        try:
            # Try different title selectors
            title = None
            
            # Try meta og:title
            og_title = soup.find('meta', property='og:title')
            if og_title and og_title.get('content'):
                return og_title['content'].strip()
            
            # Try h1
            h1 = soup.find('h1')
            if h1:
                return h1.get_text().strip()
            
            # Try title tag
            title_tag = soup.find('title')
            if title_tag:
                return title_tag.get_text().strip()
            
            return 'No title found'
            
        except Exception as e:
            logger.error(f"Error extracting title: {e}")
            return ''
    
    def _extract_text(self, soup):
        """Extract article text from parsed HTML"""
        try:
            # Remove script and style elements
            for script in soup(['script', 'style', 'nav', 'footer', 'header']):
                script.decompose()
            
            # Try to find article/main content
            article_text = ''
            
            # Try common article selectors
            selectors = [
                'article',
                '[class*="article"]',
                '[class*="content"]',
                '[class*="post"]',
                'main',
                '[class*="story"]'
            ]
            
            for selector in selectors:
                article = soup.select_one(selector)
                if article:
                    # Get all paragraphs
                    paragraphs = article.find_all('p')
                    if paragraphs:
                        article_text = ' '.join([p.get_text().strip() for p in paragraphs])
                        if len(article_text) > 100:
                            break
            
            # If still no content, try all paragraphs
            if len(article_text) < 100:
                paragraphs = soup.find_all('p')
                article_text = ' '.join([p.get_text().strip() for p in paragraphs])
            
            # Clean up text
            article_text = ' '.join(article_text.split())
            
            return article_text
            
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return ''
    
    def _extract_author(self, soup):
        """Extract article author from parsed HTML"""
        try:
            # Try meta author
            author_meta = soup.find('meta', attrs={'name': 'author'})
            if author_meta and author_meta.get('content'):
                return author_meta['content'].strip()
            
            # Try common author selectors
            author_selectors = [
                '[class*="author"]',
                '[rel="author"]',
                '[itemprop="author"]'
            ]
            
            for selector in author_selectors:
                author = soup.select_one(selector)
                if author:
                    return author.get_text().strip()
            
            return 'Unknown'
            
        except Exception as e:
            logger.error(f"Error extracting author: {e}")
            return 'Unknown'
    
    def _extract_date(self, soup):
        """Extract publish date from parsed HTML"""
        try:
            # Try meta publish date
            date_meta = soup.find('meta', property='article:published_time')
            if date_meta and date_meta.get('content'):
                return date_meta['content'].strip()
            
            # Try time tag
            time_tag = soup.find('time')
            if time_tag:
                datetime = time_tag.get('datetime')
                if datetime:
                    return datetime.strip()
                return time_tag.get_text().strip()
            
            return 'Unknown'
            
        except Exception as e:
            logger.error(f"Error extracting date: {e}")
            return 'Unknown'
