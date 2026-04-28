# TruthLens AI  - Real-Time Fake News Detector

A production-ready, full-stack AI-powered fake news detection system built with Flask, Machine Learning, and modern web technologies.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![Machine Learning](https://img.shields.io/badge/ML-Scikit--learn-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

##  Features

### Core Functionality
-  **Text Analysis**: Paste news article text for instant analysis
-  **URL Scraping**: Automatically extract content from news URLs
-  **Machine Learning**: Advanced Logistic Regression with TF-IDF vectorization
-  **Sentiment Analysis**: Detect emotional tone of articles
-  **Confidence Scoring**: Get prediction confidence percentages
-  **Real-time Processing**: Fast analysis with optimized ML pipeline

### Admin Dashboard
-  **Statistics Overview**: Total predictions, fake vs real counts
-  **Visual Analytics**: Interactive charts and graphs
-  **Recent History**: View latest predictions
-  **Auto-refresh**: Real-time dashboard updates
-  **Secure Login**: Protected admin area

### Technical Features
-  **Glassmorphism UI**: Modern, beautiful interface with Tailwind CSS
-  **Responsive Design**: Works on desktop, tablet, and mobile
-  **Production Ready**: Proper error handling and validation
-  **MySQL Database**: Persistent storage for all predictions
-  **Session Management**: Secure user authentication
-  **Modular Architecture**: Clean, maintainable code structure


##  Quick Start

### Prerequisites

- Python 3.8 or higher
- MySQL 5.7 or higher
- pip (Python package manager)

### Installation

1. **Clone or Download the Project**
   ```bash
   cd "F:\PROJECT'S\Fake_News"
   ```

2. **Create Virtual Environment** (Recommended)
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup MySQL Database**
   
   Open MySQL and run:
   ```bash
   mysql -u root -p < database_schema.sql
   ```
   
   Or manually:
   ```sql
   CREATE DATABASE truthlens_db;
   USE truthlens_db;
   -- Then copy and paste the schema from database_schema.sql
   ```

5. **Configure Database Connection**
   
   Edit `config.py` or set environment variables:
   ```python
   MYSQL_HOST = 'localhost'
   MYSQL_USER = 'root'
   MYSQL_PASSWORD = 'your_password'
   MYSQL_DATABASE = 'truthlens_db'
   ```

6. **Train the ML Model**
   ```bash
   cd ml_training
   python train_model.py
   cd ..
   ```
   
   This will:
   - Create a sample dataset (or use your own)
   - Train the Logistic Regression model
   - Save model and vectorizer to `models/` directory

7. **Run the Application**
   ```bash
   python run.py
   ```

8. **Access the Application**
   - Main Page: http://localhost:5000
   - Admin Login: http://localhost:5000/login
   - Dashboard: http://localhost:5000/dashboard

### Default Admin Credentials
```
Username: admin
Password: admin123
```
** IMPORTANT: Change these credentials in production!**

##  Usage Guide

### Analyzing News

1. **Using Text Input**
   - Click "Paste Text" button
   - Enter at least 50 characters of news text
   - Click "Analyze News"
   - View results with confidence score and sentiment

2. **Using URL Input**
   - Click "Enter URL" button
   - Paste the full URL of a news article
   - Click "Analyze News"
   - System automatically scrapes and analyzes content

### Admin Dashboard

1. Navigate to `/login`
2. Enter admin credentials
3. View comprehensive statistics:
   - Total predictions count
   - Fake vs Real news distribution
   - Average confidence scores
   - Interactive charts
   - Recent predictions history

##  Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-change-this
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=truthlens_db
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secure_password
```

### Configuration Options

Edit `config.py` for advanced settings:

- **Session timeout**: `PERMANENT_SESSION_LIFETIME`
- **Model paths**: `MODEL_PATH`, `VECTORIZER_PATH`
- **Rate limiting**: `RATE_LIMIT`
- **Debug mode**: `DEBUG`

##  Machine Learning Details

### Model Architecture
- **Algorithm**: Logistic Regression
- **Vectorization**: TF-IDF (Term Frequency-Inverse Document Frequency)
- **Features**: 5000 max features
- **N-gram Range**: (1, 2)
- **Preprocessing**:
  - Lowercase conversion
  - URL removal
  - Special character removal
  - Stopword removal
  - Tokenization

### Training Process

The model training includes:
1. Text preprocessing with NLP techniques
2. Feature extraction using TF-IDF
3. Train-test split (80-20)
4. Model training with Logistic Regression
5. Evaluation metrics (accuracy, precision, recall)
6. Model and vectorizer serialization

### Model Performance

*Note: Performance depends on the training dataset. The included sample dataset is for demonstration only.*

For production use:
- Use a large, balanced dataset (e.g., Kaggle Fake News datasets)
- Consider datasets like:
  - LIAR dataset
  - FakeNewsNet
  - ISOT Fake News Dataset

##  UI Features

### Design Elements
- **Glassmorphism**: Modern frosted glass effect
- **Smooth Animations**: Fade-in, slide-up effects
- **Responsive Layout**: Mobile-first design
- **Dark Theme**: Eye-friendly dark interface
- **Interactive Charts**: Powered by Chart.js
- **Loading States**: Visual feedback for all actions

### Color Scheme
- Primary: Indigo (#6366f1)
- Secondary: Purple (#8b5cf6)
- Accent: Pink (#ec4899)
- Success: Green (#10b981)
- Error: Red (#ef4444)

##  Security Features

- Session-based authentication
- Password hashing (production ready)
- SQL injection protection
- XSS prevention
- Input validation
- CORS configuration
- Secure cookie settings

##  Database Schema

### Tables

**users**
- id, username, password_hash, email, is_admin
- created_at, last_login

**predictions**
- id, input_text, input_url, prediction, confidence
- sentiment, sentiment_score, user_ip, user_agent
- processing_time, timestamp

##  Troubleshooting

### Common Issues

**1. Module Not Found Error**
```bash
pip install -r requirements.txt
```

**2. Database Connection Error**
- Check MySQL is running
- Verify credentials in `config.py`
- Ensure database exists

**3. Model Files Not Found**
- Run `python ml_training/train_model.py`
- Check `models/` directory exists

**4. NLTK Data Missing**
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

**5. Port Already in Use**
```bash
# Change port in run.py
app.run(port=5001)
```

##  Deployment

### Production Checklist

- [ ] Change default admin credentials
- [ ] Set strong `SECRET_KEY`
- [ ] Use production database
- [ ] Enable HTTPS
- [ ] Set `FLASK_ENV=production`
- [ ] Configure firewall
- [ ] Set up reverse proxy (Nginx)
- [ ] Enable logging
- [ ] Setup monitoring
- [ ] Regular backups

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Docker Deployment

```dockerfile
# Dockerfile example
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
```

##  Future Enhancements

- [ ] Multi-language support
- [ ] Deep learning models (BERT, GPT)
- [ ] Browser extension
- [ ] API rate limiting
- [ ] User registration system
- [ ] Export reports feature
- [ ] Email notifications
- [ ] Advanced analytics
- [ ] A/B testing for models

##  Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

##  License

This project is licensed under the MIT License.

