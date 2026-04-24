/**
 * TruthLens AI - Dashboard JavaScript
 * Handles user management and search history
 */

/**
 * Load dashboard data
 */
async function loadDashboard() {
    try {
        // Load model evaluation metrics
        await loadModelEvaluation();
        
        // Load users and search history
        await loadUsers();
        await loadSearchHistory();
        
        // Hide loading, show content
        document.getElementById('loadingIndicator').classList.add('hidden');
        document.getElementById('dashboardContent').classList.remove('hidden');
        
    } catch (error) {
        console.error('Dashboard error:', error);
        alert('Failed to load dashboard: ' + error.message);
    }
}

/**
 * Logout function
 */
async function logout() {
    try {
        const response = await fetch('/api/logout', {
            method: 'POST'
        });
        
        if (response.ok) {
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('Logout error:', error);
    }
}

/**
 * Load model evaluation metrics
 */
async function loadModelEvaluation() {
    const loadingEl = document.getElementById('modelMetricsLoading');
    const errorEl = document.getElementById('modelMetricsError');
    const contentEl = document.getElementById('modelMetricsContent');
    
    try {
        const response = await fetch('/api/model-evaluation');
        const data = await response.json();
        
        if (!response.ok || !data.success) {
            console.error('Failed to load model evaluation:', data.error);
            loadingEl.classList.add('hidden');
            errorEl.classList.remove('hidden');
            return;
        }
        
        const metrics = data.metrics;
        
        // Update metric cards
        document.getElementById('metricAccuracy').textContent = (metrics.test_accuracy * 100).toFixed(2) + '%';
        document.getElementById('metricPrecision').textContent = (metrics.precision * 100).toFixed(2) + '%';
        document.getElementById('metricRecall').textContent = (metrics.recall * 100).toFixed(2) + '%';
        document.getElementById('metricF1').textContent = (metrics.f1_score * 100).toFixed(2) + '%';
        
        // Update confusion matrix
        // metrics.confusion_matrix is [[TN, FP], [FN, TP]]
        const cm = metrics.confusion_matrix;
        document.getElementById('cmTrueNegative').textContent = cm[0][0];
        document.getElementById('cmFalsePositive').textContent = cm[0][1];
        document.getElementById('cmFalseNegative').textContent = cm[1][0];
        document.getElementById('cmTruePositive').textContent = cm[1][1];
        
        // Update model information
        document.getElementById('trainSize').textContent = metrics.train_size;
        document.getElementById('testSize').textContent = metrics.test_size;
        document.getElementById('trainAccuracy').textContent = (metrics.train_accuracy * 100).toFixed(2) + '%';
        
        // Format trained date
        const trainedDate = new Date(metrics.trained_date);
        document.getElementById('trainedDate').textContent = trainedDate.toLocaleString();
        
        // Show content, hide loading
        loadingEl.classList.add('hidden');
        contentEl.classList.remove('hidden');
        
    } catch (error) {
        console.error('Error loading model evaluation:', error);
        loadingEl.classList.add('hidden');
        errorEl.classList.remove('hidden');
    }
}

/**
 * Load registered users
 */
async function loadUsers() {
    try {
        const response = await fetch('/api/users');
        const data = await response.json();
        
        if (!response.ok || !data.success) {
            console.error('Failed to load users:', data.error);
            return;
        }
        
        const tbody = document.getElementById('usersTable');
        tbody.innerHTML = '';
        
        // Populate user filter dropdown
        const userFilter = document.getElementById('userFilter');
        const currentFilter = userFilter.value;
        userFilter.innerHTML = '<option value="">All Users</option>';
        
        if (!data.users || data.users.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center text-gray-400 py-4">No users found</td></tr>';
            return;
        }
        
        data.users.forEach(user => {
            // Add to filter dropdown
            const option = document.createElement('option');
            option.value = user.username;
            option.textContent = user.username;
            if (user.username === currentFilter) option.selected = true;
            userFilter.appendChild(option);
            
            // Create table row
            const row = document.createElement('tr');
            row.className = 'border-b border-white/5 hover:bg-white/5';
            
            const roleClass = user.is_admin ? 'text-yellow-400' : 'text-blue-400';
            const roleIcon = user.is_admin ? 'fa-crown' : 'fa-user';
            const lastLogin = user.last_login ? new Date(user.last_login).toLocaleString() : 'Never';
            
            row.innerHTML = `
                <td class="py-3 px-2 text-white font-semibold">${user.username}</td>
                <td class="py-3 px-2 text-gray-300">${user.email || 'N/A'}</td>
                <td class="py-3 px-2 ${roleClass}">
                    <i class="fas ${roleIcon} mr-1"></i>${user.is_admin ? 'Admin' : 'User'}
                </td>
                <td class="py-3 px-2 text-gray-300">${user.prediction_count || 0}</td>
                <td class="py-3 px-2 text-gray-300">${new Date(user.created_at).toLocaleDateString()}</td>
                <td class="py-3 px-2 text-gray-300">${lastLogin}</td>
                <td class="py-3 px-2">
                    <button onclick="viewUserHistory('${user.username}')" 
                            class="text-primary hover:text-blue-300 transition">
                        <i class="fas fa-eye mr-1"></i>View History
                    </button>
                </td>
            `;
            
            tbody.appendChild(row);
        });
        
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

/**
 * Load search history
 */
async function loadSearchHistory(username = '') {
    try {
        const url = username ? `/api/search-history?username=${encodeURIComponent(username)}` : '/api/search-history';
        const response = await fetch(url);
        const data = await response.json();
        
        if (!response.ok || !data.success) {
            console.error('Failed to load search history:', data.error);
            return;
        }
        
        const tbody = document.getElementById('searchHistoryTable');
        tbody.innerHTML = '';
        
        if (!data.history || data.history.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center text-gray-400 py-4">No search history found</td></tr>';
            return;
        }
        
        data.history.forEach(item => {
            const row = document.createElement('tr');
            row.className = 'border-b border-white/5 hover:bg-white/5';
            
            const predictionClass = item.prediction === 'FAKE' ? 'text-red-400' : 'text-green-400';
            const predictionIcon = item.prediction === 'FAKE' ? 'fa-exclamation-triangle' : 'fa-check-circle';
            
            row.innerHTML = `
                <td class="py-3 px-2 text-white font-semibold">${item.username || 'Anonymous'}</td>
                <td class="py-3 px-2 text-gray-300" style="max-width: 300px;">
                    <div class="truncate" title="${item.text_preview}">${item.text_preview}</div>
                </td>
                <td class="py-3 px-2 text-gray-300" style="max-width: 200px;">
                    ${item.input_url ? `<a href="${item.input_url}" target="_blank" class="text-blue-400 hover:underline truncate block">${item.input_url}</a>` : 'N/A'}
                </td>
                <td class="py-3 px-2 ${predictionClass}">
                    <i class="fas ${predictionIcon} mr-1"></i>${item.prediction}
                </td>
                <td class="py-3 px-2 text-gray-300">${item.confidence}%</td>
                <td class="py-3 px-2 text-gray-300">${new Date(item.timestamp).toLocaleString()}</td>
            `;
            
            tbody.appendChild(row);
        });
        
    } catch (error) {
        console.error('Error loading search history:', error);
    }
}

/**
 * Filter search history by user
 */
function filterSearchHistory() {
    const username = document.getElementById('userFilter').value;
    loadSearchHistory(username);
}

/**
 * View specific user's history
 */
function viewUserHistory(username) {
    const userFilter = document.getElementById('userFilter');
    userFilter.value = username;
    loadSearchHistory(username);
    
    // Scroll to search history section
    document.getElementById('searchHistoryTable').parentElement.parentElement.scrollIntoView({ behavior: 'smooth' });
}

/**
 * Start model training
 */
let trainingInterval = null;
let selectedFile = null;

/**
 * Handle file selection
 */
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        selectedFile = file;
        document.getElementById('fileName').textContent = file.name;
        document.getElementById('fileInfo').classList.remove('hidden');
        document.getElementById('uploadButton').classList.remove('hidden');
    }
}

/**
 * Upload dataset
 */
async function uploadDataset() {
    if (!selectedFile) {
        alert('Please select a file first');
        return;
    }
    
    try {
        const uploadButton = document.getElementById('uploadButton');
        uploadButton.disabled = true;
        uploadButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Uploading...';
        
        // Create form data
        const formData = new FormData();
        formData.append('dataset', selectedFile);
        
        // Upload file
        const response = await fetch('/api/upload-dataset', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok || !data.success) {
            throw new Error(data.error || 'Failed to upload dataset');
        }
        
        alert(`Dataset uploaded successfully!\n${data.message}\n\nYou can now train the model with this dataset.`);
        
        // Reset file input
        document.getElementById('datasetFile').value = '';
        selectedFile = null;
        document.getElementById('fileInfo').classList.add('hidden');
        document.getElementById('uploadButton').classList.add('hidden');
        
        uploadButton.disabled = false;
        uploadButton.innerHTML = '<i class="fas fa-cloud-upload-alt mr-2"></i>Upload Dataset';
        
    } catch (error) {
        console.error('Error uploading dataset:', error);
        alert('Failed to upload dataset: ' + error.message);
        
        const uploadButton = document.getElementById('uploadButton');
        uploadButton.disabled = false;
        uploadButton.innerHTML = '<i class="fas fa-cloud-upload-alt mr-2"></i>Upload Dataset';
    }
}

async function startTraining() {
    try {
        const trainButton = document.getElementById('trainButton');
        
        // Confirm action
        if (!confirm('Are you sure you want to retrain the model? This will replace the current model.')) {
            return;
        }
        
        // Hide results/errors from previous training
        document.getElementById('trainingResults').classList.add('hidden');
        document.getElementById('trainingError').classList.add('hidden');
        
        // Disable button
        trainButton.disabled = true;
        trainButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Starting Training...';
        trainButton.classList.add('opacity-50', 'cursor-not-allowed');
        
        // Start training
        const response = await fetch('/api/train-model', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (!response.ok || !data.success) {
            throw new Error(data.error || 'Failed to start training');
        }
        
        // Start polling for status
        startTrainingStatusPolling();
        
    } catch (error) {
        console.error('Error starting training:', error);
        alert('Failed to start training: ' + error.message);
        
        // Re-enable button
        const trainButton = document.getElementById('trainButton');
        trainButton.disabled = false;
        trainButton.innerHTML = '<i class="fas fa-brain mr-2"></i>Start Training';
        trainButton.classList.remove('opacity-50', 'cursor-not-allowed');
    }
}

/**
 * Start polling for training status
 */
function startTrainingStatusPolling() {
    // Clear any existing interval
    if (trainingInterval) {
        clearInterval(trainingInterval);
    }
    
    // Poll every 2 seconds
    trainingInterval = setInterval(checkTrainingStatus, 2000);
    
    // Check immediately
    checkTrainingStatus();
}

/**
 * Check training status
 */
async function checkTrainingStatus() {
    try {
        const response = await fetch('/api/training-status');
        const data = await response.json();
        
        if (!response.ok || !data.success) {
            console.error('Failed to get training status:', data.error);
            return;
        }
        
        const status = data.status;
        
        // Update UI
        updateTrainingUI(status);
        
        // If training is complete or failed, stop polling
        if (!status.is_training) {
            if (trainingInterval) {
                clearInterval(trainingInterval);
                trainingInterval = null;
            }
            
            // Re-enable button
            const trainButton = document.getElementById('trainButton');
            trainButton.disabled = false;
            trainButton.innerHTML = '<i class="fas fa-brain mr-2"></i>Start Training';
            trainButton.classList.remove('opacity-50', 'cursor-not-allowed');
            
            // Show results or error
            if (status.status === 'completed') {
                showTrainingResults(status);
            } else if (status.status === 'failed') {
                showTrainingError(status);
            }
        }
        
    } catch (error) {
        console.error('Error checking training status:', error);
    }
}

/**
 * Update training UI with status
 */
function updateTrainingUI(status) {
    // Update status text
    const statusEl = document.getElementById('trainingStatus');
    statusEl.textContent = status.status.charAt(0).toUpperCase() + status.status.slice(1);
    
    // Update status color
    statusEl.className = 'text-white font-semibold';
    if (status.status === 'training') {
        statusEl.classList.add('text-yellow-400');
    } else if (status.status === 'completed') {
        statusEl.classList.add('text-green-400');
    } else if (status.status === 'failed') {
        statusEl.classList.add('text-red-400');
    }
    
    // Update progress
    const progressEl = document.getElementById('trainingProgress');
    progressEl.textContent = status.progress + '%';
    
    const progressBar = document.getElementById('trainingProgressBar');
    progressBar.style.width = status.progress + '%';
    
    // Update message
    const messageEl = document.getElementById('trainingMessage');
    const icon = status.is_training ? '<i class="fas fa-spinner fa-spin mr-1"></i>' : '<i class="fas fa-info-circle mr-1"></i>';
    messageEl.innerHTML = icon + status.message;
}

/**
 * Show training results
 */
function showTrainingResults(status) {
    if (status.metrics) {
        const metrics = status.metrics;
        
        document.getElementById('resultAccuracy').textContent = (metrics.test_accuracy * 100).toFixed(2) + '%';
        document.getElementById('resultPrecision').textContent = (metrics.precision * 100).toFixed(2) + '%';
        document.getElementById('resultRecall').textContent = (metrics.recall * 100).toFixed(2) + '%';
        document.getElementById('resultF1').textContent = (metrics.f1_score * 100).toFixed(2) + '%';
        
        document.getElementById('trainingResults').classList.remove('hidden');
    }
}

/**
 * Show training error
 */
function showTrainingError(status) {
    const errorEl = document.getElementById('trainingError');
    const errorMessageEl = document.getElementById('trainingErrorMessage');
    
    errorMessageEl.textContent = status.error || 'An unknown error occurred during training.';
    errorEl.classList.remove('hidden');
}

/**
 * Initialize dashboard
 */
document.addEventListener('DOMContentLoaded', () => {
    // Load dashboard data
    loadDashboard();
    
    console.log('Dashboard initialized');
});
