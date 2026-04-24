"""
Text Preprocessing and Sentiment Analysis
Handles text cleaning and sentiment detection
"""

import re
import logging
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Configure logging
logger = logging.getLogger(__name__)

# Download NLTK data (done silently)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)


class TextProcessor:
    """Class for text preprocessing and analysis"""
    
    def __init__(self):
        """Initialize text processor with stopwords"""
        self.stop_words = set(stopwords.words('english'))
    
    def clean_text(self, text):
        """
        Clean and preprocess text
        
        Args:
            text: Raw text input
            
        Returns:
            Cleaned text string
        """
        if not text or text.strip() == '':
            return ''
        
        try:
            # Convert to lowercase
            text = str(text).lower()
            
            # Remove URLs
            text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
            
            # Remove email addresses
            text = re.sub(r'\S+@\S+', '', text)
            
            # Remove mentions and hashtags
            text = re.sub(r'@\w+|#\w+', '', text)
            
            # Remove special characters but keep spaces
            text = re.sub(r'[^a-zA-Z\s]', '', text)
            
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            return text
            
        except Exception as e:
            logger.error(f"❌ Error cleaning text: {e}")
            return text
    
    def remove_stopwords(self, text):
        """
        Remove stopwords from text
        
        Args:
            text: Cleaned text
            
        Returns:
            Text without stopwords
        """
        try:
            # Tokenize
            tokens = word_tokenize(text)
            
            # Remove stopwords and short words
            filtered_tokens = [
                word for word in tokens 
                if word not in self.stop_words and len(word) > 2
            ]
            
            return ' '.join(filtered_tokens)
            
        except Exception as e:
            logger.error(f"❌ Error removing stopwords: {e}")
            return text
    
    def preprocess(self, text):
        """
        Complete preprocessing pipeline
        
        Args:
            text: Raw text input
            
        Returns:
            Fully preprocessed text
        """
        # Clean text
        text = self.clean_text(text)
        
        # Remove stopwords
        text = self.remove_stopwords(text)
        
        return text
    
    def analyze_sentiment(self, text):
        """
        Perform sentiment analysis on text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment and polarity score
        """
        try:
            # Create TextBlob object
            blob = TextBlob(text)
            
            # Get polarity score (-1 to 1)
            polarity = blob.sentiment.polarity
            
            # Determine sentiment category
            if polarity > 0.1:
                sentiment = "Positive"
            elif polarity < -0.1:
                sentiment = "Negative"
            else:
                sentiment = "Neutral"
            
            return {
                'sentiment': sentiment,
                'polarity': round(polarity, 2),
                'subjectivity': round(blob.sentiment.subjectivity, 2)
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing sentiment: {e}")
            return {
                'sentiment': 'Unknown',
                'polarity': 0.0,
                'subjectivity': 0.0
            }
    
    def extract_keywords(self, text, top_n=10):
        """
        Extract top keywords from text
        
        Args:
            text: Input text
            top_n: Number of keywords to extract
            
        Returns:
            List of top keywords
        """
        try:
            # Tokenize and filter
            tokens = word_tokenize(text.lower())
            tokens = [
                word for word in tokens 
                if word not in self.stop_words and len(word) > 3 and word.isalpha()
            ]
            
            # Count frequency
            word_freq = {}
            for word in tokens:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Sort by frequency
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            
            # Return top N
            return [word for word, freq in sorted_words[:top_n]]
            
        except Exception as e:
            logger.error(f"❌ Error extracting keywords: {e}")
            return []
    
    def get_text_stats(self, text):
        """
        Get basic statistics about the text
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with text statistics
        """
        try:
            words = text.split()
            sentences = text.split('.')
            
            return {
                'character_count': len(text),
                'word_count': len(words),
                'sentence_count': len(sentences),
                'avg_word_length': round(sum(len(word) for word in words) / len(words), 2) if words else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating text stats: {e}")
            return {
                'character_count': 0,
                'word_count': 0,
                'sentence_count': 0,
                'avg_word_length': 0
            }
