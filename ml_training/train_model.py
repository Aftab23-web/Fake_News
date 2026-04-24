"""
Machine Learning Model Training Script
Trains a Logistic Regression model for fake news detection
Uses TF-IDF vectorization and saves the trained model
"""

import pandas as pd
import numpy as np
import pickle
import os
import sys
import json
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, precision_score, recall_score, f1_score
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download required NLTK data
print("Downloading NLTK data...")
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

class FakeNewsModelTrainer:
    """Class to handle model training for fake news detection"""
    
    def __init__(self):
        self.vectorizer = None
        self.model = None
        self.stop_words = set(stopwords.words('english'))
        
    def preprocess_text(self, text):
        """
        Preprocess text data using NLP techniques
        - Convert to lowercase
        - Remove URLs, mentions, hashtags
        - Remove special characters and numbers
        - Remove stopwords
        - Tokenize
        """
        if pd.isna(text) or text == '':
            return ''
        
        # Convert to lowercase
        text = str(text).lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove mentions and hashtags
        text = re.sub(r'@\w+|#\w+', '', text)
        
        # Remove special characters and numbers
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and short words
        tokens = [word for word in tokens if word not in self.stop_words and len(word) > 2]
        
        return ' '.join(tokens)
    
    def load_data(self, csv_path):
        """Load and preprocess the dataset"""
        print(f"\nLoading dataset from {csv_path}...")
        
        # Try to load the dataset
        try:
            df = pd.read_csv(csv_path)
            print(f"Dataset loaded successfully! Shape: {df.shape}")
            print(f"Columns: {df.columns.tolist()}")
        except FileNotFoundError:
            print(f"\n⚠️  Dataset file not found at: {csv_path}")
            print("\nCreating a sample dataset for demonstration...")
            df = self.create_sample_dataset()
        
        return df
    
    def create_sample_dataset(self):
        """Create a sample dataset for demonstration purposes"""
        # Sample fake news (labeled as 1)
        fake_news = [
            "BREAKING: Scientists discover that Earth is actually flat, NASA admits decades of lies!",
            "SHOCKING: Billionaire reveals secret to becoming rich overnight with this one trick!",
            "Aliens have been living among us for decades, government finally admits!",
            "New study shows that drinking 10 cups of coffee daily makes you immortal!",
            "URGENT: Your phone is listening to everything you say, delete it now!",
            "Celebrity reveals shocking secret: they are actually a robot from the future!",
            "Government plans to replace all birds with surveillance drones by next year!",
            "Miracle cure discovered: this simple fruit can cure all diseases!",
            "BREAKING: Time travel is real and you can do it with this simple method!",
            "Scientists confirm chocolate is better than vegetables for weight loss!",
        ]
        
        # Sample real news (labeled as 0)
        real_news = [
            "New climate report shows significant increase in global temperatures over past decade.",
            "Stock markets show volatility amid concerns about inflation and interest rates.",
            "Research team develops new vaccine that shows promise in clinical trials.",
            "Government announces infrastructure investment plan to modernize transportation.",
            "Study reveals correlation between exercise and improved mental health outcomes.",
            "Tech company releases quarterly earnings report, revenue exceeds expectations.",
            "International summit brings together leaders to discuss economic cooperation.",
            "New archaeological discovery sheds light on ancient civilization practices.",
            "University researchers publish findings on renewable energy efficiency improvements.",
            "Healthcare officials recommend updated guidelines for disease prevention.",
        ]
        
        # Create DataFrame
        texts = fake_news + real_news
        labels = [1] * len(fake_news) + [0] * len(real_news)
        
        df = pd.DataFrame({
            'text': texts,
            'label': labels
        })
        
        # Add more samples by creating variations
        expanded_texts = []
        expanded_labels = []
        
        for text, label in zip(texts, labels):
            expanded_texts.append(text)
            expanded_labels.append(label)
            
            # Create variations
            words = text.split()
            if len(words) > 5:
                # Create variation by shuffling middle part
                variation = ' '.join(words[:2] + words[2:-2] + words[-2:])
                expanded_texts.append(variation)
                expanded_labels.append(label)
        
        df = pd.DataFrame({
            'text': expanded_texts,
            'label': expanded_labels
        })
        
        print(f"✅ Sample dataset created with {len(df)} entries")
        return df
    
    def train(self, csv_path='fake_news_dataset.csv'):
        """Train the fake news detection model"""
        
        # Load data
        df = self.load_data(csv_path)
        
        # Preprocess text
        print("\nPreprocessing text data...")
        df['processed_text'] = df['text'].apply(self.preprocess_text)
        
        # Remove empty entries
        df = df[df['processed_text'] != '']
        
        # Split data
        X = df['processed_text']
        y = df['label']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"Training set size: {len(X_train)}")
        print(f"Testing set size: {len(X_test)}")
        
        # Create TF-IDF vectorizer
        print("\nCreating TF-IDF vectorizer...")
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            min_df=2,
            max_df=0.8,
            ngram_range=(1, 2)
        )
        
        # Transform text to TF-IDF features
        X_train_tfidf = self.vectorizer.fit_transform(X_train)
        X_test_tfidf = self.vectorizer.transform(X_test)
        
        print(f"TF-IDF feature matrix shape: {X_train_tfidf.shape}")
        
        # Train Logistic Regression model
        print("\nTraining Logistic Regression model...")
        self.model = LogisticRegression(
            max_iter=1000,
            random_state=42,
            C=1.0,
            solver='liblinear'
        )
        
        self.model.fit(X_train_tfidf, y_train)
        
        # Evaluate model
        print("\n" + "="*50)
        print("MODEL EVALUATION")
        print("="*50)
        
        # Training accuracy
        train_pred = self.model.predict(X_train_tfidf)
        train_accuracy = accuracy_score(y_train, train_pred)
        print(f"\n✅ Training Accuracy: {train_accuracy*100:.2f}%")
        
        # Testing accuracy
        test_pred = self.model.predict(X_test_tfidf)
        test_accuracy = accuracy_score(y_test, test_pred)
        print(f"✅ Testing Accuracy: {test_accuracy*100:.2f}%")
        
        # Calculate additional metrics
        precision = precision_score(y_test, test_pred, average='weighted')
        recall = recall_score(y_test, test_pred, average='weighted')
        f1 = f1_score(y_test, test_pred, average='weighted')
        
        # Classification report
        print("\n📊 Classification Report:")
        print(classification_report(y_test, test_pred, target_names=['REAL', 'FAKE']))
        
        # Confusion matrix
        print("\n🔍 Confusion Matrix:")
        cm = confusion_matrix(y_test, test_pred)
        print(f"    Predicted REAL  Predicted FAKE")
        print(f"Actually REAL:  {cm[0][0]:5d}         {cm[0][1]:5d}")
        print(f"Actually FAKE:  {cm[1][0]:5d}         {cm[1][1]:5d}")
        
        # Store evaluation metrics for later use
        self.evaluation_metrics = {
            'train_accuracy': float(train_accuracy),
            'test_accuracy': float(test_accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'confusion_matrix': cm.tolist(),
            'trained_date': datetime.now().isoformat(),
            'train_size': len(X_train),
            'test_size': len(X_test)
        }
        
        return train_accuracy, test_accuracy
    
    def save_models(self, model_dir='../models'):
        """Save trained model and vectorizer"""
        
        # Create models directory if it doesn't exist
        os.makedirs(model_dir, exist_ok=True)
        
        model_path = os.path.join(model_dir, 'model.pkl')
        vectorizer_path = os.path.join(model_dir, 'vectorizer.pkl')
        
        # Save model
        with open(model_path, 'wb') as f:
            pickle.dump(self.model, f)
        print(f"\n✅ Model saved to: {model_path}")
        
        # Save vectorizer
        with open(vectorizer_path, 'wb') as f:
            pickle.dump(self.vectorizer, f)
        print(f"✅ Vectorizer saved to: {vectorizer_path}")
        
        # Save evaluation metrics to JSON
        if hasattr(self, 'evaluation_metrics'):
            metrics_path = os.path.join(model_dir, 'evaluation_metrics.json')
            with open(metrics_path, 'w') as f:
                json.dump(self.evaluation_metrics, f, indent=4)
            print(f"✅ Evaluation metrics saved to: {metrics_path}")
        
        # Save model info
        info_path = os.path.join(model_dir, 'model_info.txt')
        with open(info_path, 'w') as f:
            f.write("TruthLens AI - Fake News Detection Model\n")
            f.write("="*50 + "\n")
            f.write("Model: Logistic Regression\n")
            f.write("Vectorizer: TF-IDF\n")
            f.write(f"Max Features: 5000\n")
            f.write(f"N-gram Range: (1, 2)\n")
            if hasattr(self, 'evaluation_metrics'):
                f.write(f"\n--- Evaluation Metrics ---\n")
                f.write(f"Test Accuracy: {self.evaluation_metrics['test_accuracy']*100:.2f}%\n")
                f.write(f"Precision: {self.evaluation_metrics['precision']*100:.2f}%\n")
                f.write(f"Recall: {self.evaluation_metrics['recall']*100:.2f}%\n")
                f.write(f"F1-Score: {self.evaluation_metrics['f1_score']*100:.2f}%\n")
                f.write(f"Trained: {self.evaluation_metrics['trained_date']}\n")
        
        print(f"✅ Model info saved to: {info_path}")


def main():
    """Main function to train and save the model"""
    
    print("="*60)
    print("TruthLens AI - Machine Learning Model Training")
    print("="*60)
    
    # Initialize trainer
    trainer = FakeNewsModelTrainer()
    
    # Train model
    csv_path = 'fake_news_dataset.csv'
    if not os.path.exists(csv_path):
        print(f"\n⚠️  Note: '{csv_path}' not found.")
        print("Creating sample dataset for demonstration purposes.")
        print("\nFor production use, please provide a real dataset with:")
        print("  - Column 'text': containing news article text")
        print("  - Column 'label': 0 for REAL news, 1 for FAKE news")
    
    train_acc, test_acc = trainer.train(csv_path)
    
    # Save models
    trainer.save_models()
    
    print("\n" + "="*60)
    print("✅ Training completed successfully!")
    print("="*60)
    print(f"\n📈 Final Results:")
    print(f"   Training Accuracy: {train_acc*100:.2f}%")
    print(f"   Testing Accuracy: {test_acc*100:.2f}%")
    print("\n🚀 Models are ready for deployment!")
    

if __name__ == '__main__':
    main()
