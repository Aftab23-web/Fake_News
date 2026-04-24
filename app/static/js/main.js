/**
 * TruthLens AI - Main JavaScript
 * Handles news analysis and user interactions
 */

// Global state
let currentInputType = 'text';

/**
 * Switch between text and URL input
 */
function switchInputType(type) {
    currentInputType = type;
    
    const textInput = document.getElementById('textInput');
    const urlInput = document.getElementById('urlInput');
    const textBtn = document.getElementById('textBtn');
    const urlBtn = document.getElementById('urlBtn');
    
    if (type === 'text') {
        textInput.classList.remove('hidden');
        urlInput.classList.add('hidden');
        textBtn.classList.add('active');
        urlBtn.classList.remove('active');
    } else {
        textInput.classList.add('hidden');
        urlInput.classList.remove('hidden');
        textBtn.classList.remove('active');
        urlBtn.classList.add('active');
    }
}

/**
 * Update character count for text input
 */
function updateCharCount() {
    const newsText = document.getElementById('newsText');
    const charCount = document.getElementById('charCount');
    
    if (newsText && charCount) {
        newsText.addEventListener('input', () => {
            charCount.textContent = newsText.value.length;
        });
    }
}

/**
 * Show error message
 */
function showError(message) {
    const errorMessage = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    
    errorText.textContent = message;
    errorMessage.classList.remove('hidden');
    
    // Scroll to error
    errorMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

/**
 * Hide error message
 */
function hideError() {
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.classList.add('hidden');
}

/**
 * Show loading indicator
 */
function showLoading(show) {
    const loadingIndicator = document.getElementById('loadingIndicator');
    const analyzeBtn = document.getElementById('analyzeBtn');
    
    if (show) {
        loadingIndicator.classList.remove('hidden');
        analyzeBtn.disabled = true;
    } else {
        loadingIndicator.classList.add('hidden');
        analyzeBtn.disabled = false;
    }
}

/**
 * Analyze news article
 */
async function analyzeNews() {
    hideError();
    
    // Get input based on current type
    let inputData = {};
    
    if (currentInputType === 'text') {
        const newsText = document.getElementById('newsText').value.trim();
        
        if (!newsText) {
            showError('Please enter some text to analyze');
            return;
        }
        
        if (newsText.length < 50) {
            showError('Text is too short. Please provide at least 50 characters.');
            return;
        }
        
        inputData.text = newsText;
    } else {
        const newsUrl = document.getElementById('newsUrl').value.trim();
        
        if (!newsUrl) {
            showError('Please enter a URL to analyze');
            return;
        }
        
        // Basic URL validation
        try {
            new URL(newsUrl);
        } catch (e) {
            showError('Please enter a valid URL (e.g., https://example.com/article)');
            return;
        }
        
        inputData.url = newsUrl;
    }
    
    // Show loading
    showLoading(true);
    
    try {
        // Send request to API
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(inputData)
        });
        
        const data = await response.json();
        
        // Check if user is not logged in (401 status)
        if (response.status === 401) {
            showError('Please login to check news authenticity');
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
            return;
        }
        
        if (!response.ok || !data.success) {
            throw new Error(data.error || 'Analysis failed');
        }
        
        // Display results
        displayResults(data);
        
    } catch (error) {
        console.error('Analysis error:', error);
        showError(error.message || 'Failed to analyze. Please try again.');
    } finally {
        showLoading(false);
    }
}

/**
 * Display analysis results
 */
function displayResults(data) {
    console.log('Full API response:', data);
    
    const resultsCard = document.getElementById('resultsCard');
    
    // Populate prediction badge
    const predictionBadge = document.getElementById('predictionBadge');
    predictionBadge.textContent = data.prediction;
    predictionBadge.className = 'inline-block px-8 py-4 rounded-2xl text-3xl font-bold mb-4';
    
    if (data.prediction === 'FAKE') {
        predictionBadge.classList.add('prediction-badge-fake');
    } else {
        predictionBadge.classList.add('prediction-badge-real');
    }
    
    // Populate confidence
    document.getElementById('confidenceText').textContent = `${data.confidence}%`;
    
    // Populate sentiment
    const sentimentText = document.getElementById('sentimentText');
    sentimentText.textContent = data.sentiment;
    sentimentText.className = 'text-2xl font-bold';
    
    if (data.sentiment === 'Positive') {
        sentimentText.classList.add('sentiment-positive');
    } else if (data.sentiment === 'Negative') {
        sentimentText.classList.add('sentiment-negative');
    } else {
        sentimentText.classList.add('sentiment-neutral');
    }
    
    // Populate probability bars
    document.getElementById('fakeProbText').textContent = `${data.fake_probability}%`;
    document.getElementById('fakeProbBar').style.width = `${data.fake_probability}%`;
    
    document.getElementById('realProbText').textContent = `${data.real_probability}%`;
    document.getElementById('realProbBar').style.width = `${data.real_probability}%`;
    
    // Populate sentiment details
    document.getElementById('sentimentCategory').textContent = data.sentiment;
    document.getElementById('polarityScore').textContent = data.sentiment_score;
    document.getElementById('subjectivityScore').textContent = data.subjectivity;
    
    // Populate text preview
    document.getElementById('textPreview').textContent = data.text_preview;
    
    // Populate influential words (Explainable AI)
    console.log('About to display influential words:', data.influential_words);
    console.log('Type:', typeof data.influential_words, 'Length:', data.influential_words ? data.influential_words.length : 'N/A');
    displayInfluentialWords(data.influential_words || [], data.prediction);
    
    // Populate processing time
    document.getElementById('processingTime').textContent = data.processing_time;
    
    // Show results card
    resultsCard.classList.remove('hidden');
    
    // Scroll to results
    resultsCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/**
 * Display influential words for Explainable AI
 */
function displayInfluentialWords(influentialWords, prediction) {
    const wordsList = document.getElementById('influentialWordsList');
    const predictionLabel = document.getElementById('influentialWordsPrediction');
    const section = document.getElementById('influentialWordsSection');
    
    console.log('Influential words received:', influentialWords);
    console.log('Prediction:', prediction);
    console.log('Is Array?', Array.isArray(influentialWords));
    
    // Set prediction label
    predictionLabel.textContent = prediction;
    predictionLabel.className = 'font-bold';
    if (prediction === 'FAKE') {
        predictionLabel.classList.add('text-red-400');
    } else {
        predictionLabel.classList.add('text-green-400');
    }
    
    // Clear previous words
    wordsList.innerHTML = '';
    
    // Check if we have influential words
    if (!influentialWords || influentialWords.length === 0) {
        console.warn('No influential words to display - empty or null');
        wordsList.innerHTML = '<p class="text-gray-400 text-sm italic">No influential words detected</p>';
        return;
    }
    
    console.log('Processing', influentialWords.length, 'words');
    
    // Find max importance for normalization
    const maxImportance = Math.max(...influentialWords.map(w => w[1]));
    console.log('Max importance:', maxImportance);
    
    // Create badges for each influential word
    influentialWords.forEach(([word, importance]) => {
        // Normalize importance to scale (0.5 to 1.0 for visual variation)
        const normalizedImportance = 0.5 + (importance / maxImportance) * 0.5;
        
        // Create badge element
        const badge = document.createElement('span');
        badge.className = 'inline-block px-3 py-1 rounded-full text-sm font-semibold transition-transform hover:scale-110 cursor-default';
        
        // Color based on prediction
        if (prediction === 'FAKE') {
            badge.classList.add('bg-red-500/30', 'text-red-200', 'border', 'border-red-400/50');
        } else {
            badge.classList.add('bg-green-500/30', 'text-green-200', 'border', 'border-green-400/50');
        }
        
        // Scale badge size based on importance
        const fontSize = 0.75 + (normalizedImportance - 0.5) * 0.5; // 0.75rem to 1rem
        badge.style.fontSize = `${fontSize}rem`;
        
        // Add opacity based on importance
        badge.style.opacity = normalizedImportance;
        
        // Set word text
        badge.textContent = word;
        
        // Add tooltip with importance score
        badge.title = `Importance: ${importance.toFixed(4)}`;
        
        // Append to container
        wordsList.appendChild(badge);
    });
}

/**
 * Reset analysis form
 */
function resetAnalysis() {
    // Clear inputs
    document.getElementById('newsText').value = '';
    document.getElementById('newsUrl').value = '';
    
    // Reset character count
    document.getElementById('charCount').textContent = '0';
    
    // Hide results
    document.getElementById('resultsCard').classList.add('hidden');
    
    // Hide errors
    hideError();
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * Initialize page
 */
document.addEventListener('DOMContentLoaded', () => {
    // Set up character count
    updateCharCount();
    
    // Enable Enter key for text area (Ctrl+Enter to submit)
    const newsText = document.getElementById('newsText');
    if (newsText) {
        newsText.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                analyzeNews();
            }
        });
    }
    
    // Enable Enter key for URL input
    const newsUrl = document.getElementById('newsUrl');
    if (newsUrl) {
        newsUrl.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                analyzeNews();
            }
        });
    }
    
    console.log('TruthLens AI initialized');
});
