"""
Machine Learning Model Handler
Loads and uses the trained model for predictions
"""

import pickle
import os
import logging
import numpy as np

# Configure logging
logger = logging.getLogger(__name__)


class MLModel:
    """Wrapper class for the ML model and vectorizer"""
    
    def __init__(self, model_path, vectorizer_path):
        """
        Initialize the ML model
        
        Args:
            model_path: Path to the saved model file
            vectorizer_path: Path to the saved vectorizer file
        """
        self.model = None
        self.vectorizer = None
        self.model_path = model_path
        self.vectorizer_path = vectorizer_path
        self._load_models()
    
    def _load_models(self):
        """Load the trained model and vectorizer from disk"""
        try:
            # Check if model files exist
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
            
            if not os.path.exists(self.vectorizer_path):
                raise FileNotFoundError(f"Vectorizer file not found: {self.vectorizer_path}")
            
            # Load model
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            logger.info("✅ Model loaded successfully")
            
            # Load vectorizer
            with open(self.vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            logger.info("✅ Vectorizer loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Error loading models: {e}")
            raise
    
    def predict(self, text):
        """
        Predict whether the news is fake or real
        
        Args:
            text: Preprocessed news text
            
        Returns:
            Dictionary with prediction and confidence
        """
        try:
            # Transform text using vectorizer
            text_vectorized = self.vectorizer.transform([text])
            
            # Get prediction
            prediction = self.model.predict(text_vectorized)[0]
            
            # Get prediction probability
            probabilities = self.model.predict_proba(text_vectorized)[0]
            
            # Determine result
            if prediction == 1:
                label = "FAKE"
                confidence = probabilities[1] * 100
            else:
                label = "REAL"
                confidence = probabilities[0] * 100
            
            return {
                'prediction': label,
                'confidence': round(confidence, 2),
                'fake_probability': round(probabilities[1] * 100, 2),
                'real_probability': round(probabilities[0] * 100, 2)
            }
            
        except Exception as e:
            logger.error(f"❌ Error during prediction: {e}")
            raise
    
    def is_loaded(self):
        """Check if models are loaded"""
        return self.model is not None and self.vectorizer is not None
    
    def get_influential_words(self, text, prediction_label, top_n=10):
        """
        Get the most influential words contributing to the prediction
        
        Args:
            text: Preprocessed news text
            prediction_label: The prediction label ('FAKE' or 'REAL')
            top_n: Number of top influential words to return
            
        Returns:
            List of tuples (word, importance_score)
        """
        try:
            logger.info(f"🔍 Getting influential words for {prediction_label} prediction")
            logger.info(f"📝 Input text length: {len(text)} chars")
            logger.info(f"📝 Input text sample: {text[:100]}...")
            
            # Transform text using vectorizer
            text_vectorized = self.vectorizer.transform([text])
            logger.info(f"📊 Vectorized shape: {text_vectorized.shape}")
            
            # Get feature names (words)
            feature_names = self.vectorizer.get_feature_names_out()
            logger.info(f"📚 Total vocabulary size: {len(feature_names)}")
            
            # Get the indices and values of non-zero features in the input
            feature_indices = text_vectorized.nonzero()[1]
            feature_values = text_vectorized.data
            logger.info(f"✅ Found {len(feature_indices)} non-zero features in input")
            
            if len(feature_indices) == 0:
                logger.warning("❌ No features found in text after vectorization")
                return []
            
            # Get model coefficients (works for logistic regression, linear SVM, etc.)
            if hasattr(self.model, 'coef_'):
                coefficients = self.model.coef_[0]
                logger.info(f"📊 Model has {len(coefficients)} coefficients")
            else:
                # For tree-based models, use feature importances
                if hasattr(self.model, 'feature_importances_'):
                    coefficients = self.model.feature_importances_
                    logger.info(f"🌲 Using feature importances: {len(coefficients)}")
                else:
                    logger.warning("⚠️ Model doesn't support feature importance extraction")
                    return []
            
            # Calculate word importance scores
            word_scores = []
            for idx, value in zip(feature_indices, feature_values):
                word = feature_names[idx]
                coef = coefficients[idx]
                
                # For FAKE prediction, we want positive coefficients (contributing to class 1)
                # For REAL prediction, we want negative coefficients (contributing to class 0)
                if prediction_label == 'FAKE':
                    importance = coef * value
                else:
                    importance = -coef * value
                
                word_scores.append((word, float(importance)))
            
            logger.info(f"💯 Calculated {len(word_scores)} word scores")
            
            # Sort by importance (descending for positive, ascending for negative)
            word_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Show top 10 for debugging
            logger.info(f"🏆 Top 10 scores (before filtering): {word_scores[:10]}")
            
            # For FAKE predictions, take top positive scores
            # For REAL predictions, also take top positive scores (we already negated them)
            positive_words = [(word, score) for word, score in word_scores if score > 0]
            logger.info(f"➕ Found {len(positive_words)} positive influential words")
            
            # If we have positive words, return them
            if len(positive_words) > 0:
                result = positive_words[:top_n]
                logger.info(f"✅ Returning top {len(result)} positive words: {result}")
                return result
            
            # If no positive words, take top words by absolute value
            logger.warning("⚠️ No positive influential words found, taking top absolute values")
            word_scores_abs = [(word, abs(score)) for word, score in word_scores]
            word_scores_abs.sort(key=lambda x: x[1], reverse=True)
            result = word_scores_abs[:top_n]
            logger.info(f"📊 Returning {len(result)} words by absolute importance: {result}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error extracting influential words: {e}", exc_info=True)
            return []
