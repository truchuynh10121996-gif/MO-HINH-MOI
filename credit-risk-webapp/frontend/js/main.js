// ===========================
// Credit Risk Assessment System
// Main JavaScript
// ===========================

// Global variables
let uploadedFile = null;
let analysisResults = null;
let barChart = null;
let radarChart = null;

const API_BASE = window.location.origin;

// ===========================
// File Upload Handling
// ===========================

const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const removeFileBtn = document.getElementById('removeFile');
const analyzeBtn = document.getElementById('analyzeBtn');
const aiAnalyzeBtn = document.getElementById('aiAnalyzeBtn');
const downloadReportBtn = document.getElementById('downloadReportBtn');

// Click to upload
uploadArea.addEventListener('click', () => {
    fileInput.click();
});

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#c2185b';
    uploadArea.style.background = 'rgba(255, 107, 157, 0.15)';
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.style.borderColor = '#ff6b9d';
    uploadArea.style.background = 'rgba(255, 107, 157, 0.05)';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#ff6b9d';
    uploadArea.style.background = 'rgba(255, 107, 157, 0.05)';

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

// File input change
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

// Remove file
removeFileBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    uploadedFile = null;
    fileInput.value = '';
    fileInfo.classList.add('d-none');
    uploadArea.classList.remove('d-none');
    analyzeBtn.disabled = true;
    resetResults();
});

function handleFileSelect(file) {
    if (!file.name.match(/\.(xlsx|xls)$/i)) {
        showAlert('Vui lòng chọn file Excel (.xlsx hoặc .xls)', 'danger');
        return;
    }

    uploadedFile = file;
    fileName.textContent = file.name;
    uploadArea.classList.add('d-none');
    fileInfo.classList.remove('d-none');
    analyzeBtn.disabled = false;
}

// ===========================
// Analysis Functions
// ===========================

analyzeBtn.addEventListener('click', async () => {
    if (!uploadedFile) return;

    showLoading(true);
    hideWelcome();

    const formData = new FormData();
    formData.append('file', uploadedFile);

    try {
        const response = await fetch(`${API_BASE}/api/upload-financial-report`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Lỗi khi phân tích file');
        }

        analysisResults = data;
        displayResults(data);
        aiAnalyzeBtn.disabled = false;
        downloadReportBtn.disabled = false;
        showAlert('Phân tích thành công!', 'success');

    } catch (error) {
        console.error('Error:', error);
        showAlert(error.message, 'danger');
    } finally {
        showLoading(false);
    }
});

function displayResults(data) {
    const { ratios, predictions, pd_classification } = data;

    // Show results container
    document.getElementById('resultsContainer').classList.remove('d-none');
    document.getElementById('resultsContainer').classList.add('fade-in');

    // Display PD Value (from Stacking model)
    const stackingPD = predictions.Stacking.pd;
    document.getElementById('pdValue').textContent = `${(stackingPD * 100).toFixed(2)}%`;
    document.getElementById('pdLabel').textContent = predictions.Stacking.label;

    // PD Classification Badge
    const badge = document.getElementById('pdBadge');
    badge.textContent = `${pd_classification.rating} - ${pd_classification.classification}`;
    badge.style.background = pd_classification.gradient_color;
    badge.className = 'badge';

    // Display all model predictions
    const modelPredictionsDiv = document.getElementById('modelPredictions');
    modelPredictionsDiv.innerHTML = '';

    for (const [modelName, result] of Object.entries(predictions)) {
        const predDiv = document.createElement('div');
        predDiv.className = 'model-pred';
        predDiv.innerHTML = `
            <span class="model-name">${modelName}:</span>
            <span class="model-pd">${(result.pd * 100).toFixed(2)}% - ${result.label}</span>
        `;
        modelPredictionsDiv.appendChild(predDiv);
    }

    // Display ratios table
    const ratiosTable = document.getElementById('ratiosTable');
    ratiosTable.innerHTML = '';

    for (const [name, value] of Object.entries(ratios)) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${name}</td>
            <td class="text-end">${value !== null ? value.toFixed(4) : 'N/A'}</td>
        `;
        ratiosTable.appendChild(row);
    }

    // Create charts
    createCharts(ratios);
}

function createCharts(ratios) {
    const labels = Object.keys(ratios);
    const values = Object.values(ratios).map(v => v !== null ? v : 0);

    // Destroy existing charts
    if (barChart) barChart.destroy();
    if (radarChart) radarChart.destroy();

    // Bar Chart
    const barCtx = document.getElementById('barChartCanvas').getContext('2d');
    barChart = new Chart(barCtx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Giá trị',
                data: values,
                backgroundColor: 'rgba(255, 107, 157, 0.7)',
                borderColor: 'rgba(194, 24, 91, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Biểu đồ Cột - 14 Chỉ số Tài chính',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    color: '#c2185b'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        autoSkip: false,
                        maxRotation: 45,
                        minRotation: 45,
                        font: {
                            size: 9
                        }
                    }
                }
            }
        }
    });

    // Radar Chart
    const radarCtx = document.getElementById('radarChartCanvas').getContext('2d');
    radarChart = new Chart(radarCtx, {
        type: 'radar',
        data: {
            labels: labels.map(l => l.replace(/\([^)]*\)/g, '').trim()), // Remove X1, X2, etc
            datasets: [{
                label: 'Giá trị',
                data: values,
                fill: true,
                backgroundColor: 'rgba(255, 107, 157, 0.2)',
                borderColor: 'rgba(255, 107, 157, 1)',
                pointBackgroundColor: 'rgba(255, 107, 157, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(255, 107, 157, 1)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Biểu đồ Radar - Phân tích Đa chiều',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    color: '#c2185b'
                }
            },
            scales: {
                r: {
                    angleLines: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    pointLabels: {
                        font: {
                            size: 10
                        }
                    },
                    ticks: {
                        backdropColor: 'transparent'
                    }
                }
            }
        }
    });
}

// ===========================
// AI Analysis
// ===========================

aiAnalyzeBtn.addEventListener('click', async () => {
    if (!analysisResults) return;

    const apiKey = document.getElementById('apiKeyInput').value.trim();

    showLoading(true);

    try {
        const formData = new FormData();
        formData.append('ratios', JSON.stringify(analysisResults.ratios));
        formData.append('predictions', JSON.stringify(analysisResults.predictions));
        if (apiKey) formData.append('api_key', apiKey);

        const response = await fetch(`${API_BASE}/api/analyze-with-ai`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Lỗi khi phân tích AI');
        }

        // Display AI analysis
        const aiAnalysisCard = document.getElementById('aiAnalysisCard');
        const aiAnalysisContent = document.getElementById('aiAnalysisContent');
        aiAnalysisContent.textContent = data.analysis;
        aiAnalysisCard.style.display = 'block';
        aiAnalysisCard.classList.add('fade-in');

        showAlert('AI đã phân tích xong!', 'success');

    } catch (error) {
        console.error('Error:', error);
        showAlert(error.message, 'danger');
    } finally {
        showLoading(false);
    }
});

// ===========================
// Download Report
// ===========================

downloadReportBtn.addEventListener('click', async () => {
    if (!analysisResults) return;

    try {
        const aiAnalysisContent = document.getElementById('aiAnalysisContent').textContent || '';
        const stackingPD = analysisResults.predictions.Stacking.pd;
        const stackingLabel = analysisResults.predictions.Stacking.label;

        const payload = {
            ratios: analysisResults.ratios,
            pd_value: stackingPD,
            pd_label: stackingLabel,
            ai_analysis: aiAnalysisContent,
            company_name: 'KHÁCH HÀNG DOANH NGHIỆP'
        };

        const response = await fetch(`${API_BASE}/api/generate-report`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error('Lỗi khi tạo báo cáo');
        }

        // Download file
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Credit_Risk_Report_${Date.now()}.docx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        showAlert('Đã tải báo cáo thành công!', 'success');

    } catch (error) {
        console.error('Error:', error);
        showAlert(error.message, 'danger');
    }
});

// ===========================
// Chat Functions
// ===========================

const chatInput = document.getElementById('chatInput');
const chatSendBtn = document.getElementById('chatSendBtn');
const chatMessages = document.getElementById('chatMessages');

chatSendBtn.addEventListener('click', sendChatMessage);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendChatMessage();
});

async function sendChatMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    // Add user message to chat
    const userMsgDiv = document.createElement('div');
    userMsgDiv.className = 'chat-message user-message';
    userMsgDiv.textContent = message;
    chatMessages.appendChild(userMsgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    chatInput.value = '';

    const apiKey = document.getElementById('apiKeyInput').value.trim();

    try {
        const formData = new FormData();
        formData.append('message', message);
        if (analysisResults) {
            formData.append('context', JSON.stringify(analysisResults));
        }
        if (apiKey) formData.append('api_key', apiKey);

        const response = await fetch(`${API_BASE}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                context: analysisResults
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Lỗi khi chat');
        }

        // Add assistant response
        const assistantMsgDiv = document.createElement('div');
        assistantMsgDiv.className = 'chat-message assistant-message';
        assistantMsgDiv.innerHTML = `<i class="fas fa-robot"></i> ${data.response}`;
        chatMessages.appendChild(assistantMsgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

    } catch (error) {
        console.error('Error:', error);
        const errorMsgDiv = document.createElement('div');
        errorMsgDiv.className = 'chat-message assistant-message';
        errorMsgDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i> Lỗi: ${error.message}`;
        chatMessages.appendChild(errorMsgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

// ===========================
// Utility Functions
// ===========================

function showLoading(show) {
    const spinner = document.getElementById('loadingSpinner');
    if (show) {
        spinner.classList.remove('d-none');
    } else {
        spinner.classList.add('d-none');
    }
}

function hideWelcome() {
    const welcome = document.getElementById('welcomeMessage');
    welcome.style.display = 'none';
}

function resetResults() {
    document.getElementById('resultsContainer').classList.add('d-none');
    document.getElementById('welcomeMessage').style.display = 'block';
    document.getElementById('aiAnalysisCard').style.display = 'none';
    analysisResults = null;
    aiAnalyzeBtn.disabled = true;
    downloadReportBtn.disabled = true;
}

function showAlert(message, type) {
    // Create Bootstrap alert
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);

    // Auto dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// ===========================
// Tab Management & News Loading
// ===========================

// Load news when tab is clicked
document.addEventListener('DOMContentLoaded', () => {
    // Listen to main tabs
    const mainTabs = document.getElementById('mainTabs');
    if (mainTabs) {
        mainTabs.addEventListener('shown.bs.tab', (e) => {
            const target = e.target.getAttribute('data-bs-target');

            // Load news when News tab or Dashboard tab is shown
            if (target === '#news') {
                loadNews('newsFullContainer');
            } else if (target === '#dashboard') {
                loadNews('newsContainer');
            }
        });
    }
});

// Load RSS news feeds
async function loadNews(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    // Show loading
    container.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Đang tải...</span>
            </div>
            <p class="mt-2">Đang tải tin tức...</p>
        </div>
    `;

    try {
        const response = await fetch(`${API_BASE}/api/rss-feeds`);
        if (!response.ok) throw new Error('Không thể tải tin tức');

        const data = await response.json();

        if (!data.articles || data.articles.length === 0) {
            container.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle"></i> Không có tin tức mới
                </div>
            `;
            return;
        }

        // Display articles
        let html = '<div class="row">';
        data.articles.forEach((article, index) => {
            const date = new Date(article.published);
            const formattedDate = date.toLocaleString('vi-VN');

            html += `
                <div class="col-md-6 mb-3">
                    <div class="news-article">
                        <div class="news-title">${article.title}</div>
                        <div class="news-time">
                            <i class="fas fa-clock"></i> ${formattedDate}
                        </div>
                        <div class="news-description mb-2">${article.description || ''}</div>
                        <a href="${article.link}" target="_blank" class="news-link">
                            <i class="fas fa-external-link-alt"></i> Đọc thêm
                        </a>
                    </div>
                </div>
            `;

            // Add row break every 2 articles
            if ((index + 1) % 2 === 0) {
                html += '</div><div class="row">';
            }
        });
        html += '</div>';

        container.innerHTML = html;

    } catch (error) {
        console.error('Error loading news:', error);
        container.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle"></i>
                Lỗi khi tải tin tức: ${error.message}
            </div>
        `;
    }
}

// Smooth tab transitions
document.querySelectorAll('.premium-tabs .nav-link').forEach(tab => {
    tab.addEventListener('click', function() {
        // Add smooth transition effect
        const tabContent = document.querySelector('.tab-content');
        if (tabContent) {
            tabContent.style.opacity = '0';
            setTimeout(() => {
                tabContent.style.opacity = '1';
            }, 150);
        }
    });
});

// ===========================
// Initialize
// ===========================

console.log('Credit Risk Assessment System - Frontend Loaded');
