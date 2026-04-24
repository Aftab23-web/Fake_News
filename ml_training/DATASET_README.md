# Training Dataset Guide

## Sample Dataset

A sample training dataset has been provided: **`sample_training_data.csv`**

This file contains 50 labeled news articles:
- **25 FAKE** news examples (label = 1)
- **25 REAL** news examples (label = 0)

## CSV Format Requirements

Your training dataset must be a CSV file with the following structure:

| Column | Description | Required |
|--------|-------------|----------|
| `text` | The news article text or headline | Yes |
| `label` | 0 = REAL news, 1 = FAKE news | Yes |

### Example:
```csv
text,label
"Government announces new infrastructure plan",0
"BREAKING: Aliens discovered living among us!",1
```

## Using Your Own Dataset

### Option 1: Via Admin Dashboard (Recommended)
1. Log in as admin
2. Go to Dashboard
3. Scroll to "Model Training Control" section
4. Click "Choose CSV File" under Dataset Upload
5. Select your CSV file (must have "text" and "label" columns)
6. Click "Upload Dataset"
7. Click "Start Training" to train the model

### Option 2: Manual Upload
1. Place your CSV file in the `ml_training/` directory
2. Rename it to `fake_news_dataset.csv`
3. Run training via dashboard or command line:
   ```bash
   cd ml_training
   python train_model.py
   ```

## Dataset Best Practices

### Size Recommendations
- **Minimum**: 100 samples (50 fake, 50 real)
- **Good**: 1,000+ samples
- **Excellent**: 10,000+ samples
- **Professional**: 100,000+ samples

### Quality Guidelines
1. **Balance**: Equal or near-equal numbers of fake and real news
2. **Diversity**: Include various topics and writing styles
3. **Length**: Mix of short headlines and longer articles
4. **Accuracy**: Ensure labels are correct
5. **Clean Data**: Remove duplicates and corrupted entries

### Finding Datasets
You can find public fake news datasets from:
- Kaggle (search "fake news dataset")
- UCI Machine Learning Repository
- GitHub repositories
- Academic research papers

## Training Process

Once you upload a dataset:
1. System validates CSV format
2. Preprocessing: Text cleaning, tokenization, stopword removal
3. Feature extraction: TF-IDF vectorization
4. Model training: Logistic Regression
5. Evaluation: Accuracy, Precision, Recall, F1-Score, Confusion Matrix
6. Model saved and automatically loaded

## Evaluation Metrics Explained

- **Accuracy**: Overall correctness (correct predictions / total predictions)
- **Precision**: Of predicted fake news, how many were actually fake
- **Recall**: Of actual fake news, how many were correctly identified
- **F1-Score**: Harmonic mean of precision and recall (balance measure)
- **Confusion Matrix**: Breakdown of correct/incorrect predictions

## Need Help?

If you encounter issues:
1. Check CSV file format (must have "text" and "label" columns)
2. Ensure labels are 0 (real) or 1 (fake)
3. Remove special characters from CSV if causing parsing errors
4. Check admin dashboard training status for detailed error messages
