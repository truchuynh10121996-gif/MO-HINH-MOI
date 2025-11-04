// ===========================
// Dashboard JavaScript
// ===========================

const API_BASE = window.location.origin;

// ===========================
// News Feed Functions
// ===========================

document.addEventListener('DOMContentLoaded', () => {
    loadRSSFeeds();
});

document.getElementById('refreshNewsBtn').addEventListener('click', () => {
    loadRSSFeeds();
});

async function loadRSSFeeds() {
    const newsLoading = document.getElementById('newsLoading');
    const newsContainer = document.getElementById('newsContainer');

    newsLoading.classList.remove('d-none');
    newsContainer.innerHTML = '';

    try {
        const response = await fetch(`${API_BASE}/api/rss-feeds`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Lỗi khi tải RSS feeds');
        }

        const feeds = data.feeds;

        // Display feeds in 2 columns
        let col1Html = '';
        let col2Html = '';
        const sources = Object.keys(feeds);

        sources.forEach((source, index) => {
            const articles = feeds[source];
            const feedHtml = createFeedHTML(source, articles);

            if (index % 2 === 0) {
                col1Html += feedHtml;
            } else {
                col2Html += feedHtml;
            }
        });

        newsContainer.innerHTML = `
            <div class="col-md-6">${col1Html}</div>
            <div class="col-md-6">${col2Html}</div>
        `;

    } catch (error) {
        console.error('Error:', error);
        newsContainer.innerHTML = `
            <div class="col-12">
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle"></i> ${error.message}
                </div>
            </div>
        `;
    } finally {
        newsLoading.classList.add('d-none');
    }
}

function createFeedHTML(source, articles) {
    let articlesHTML = '';

    articles.forEach(article => {
        articlesHTML += `
            <div class="news-article mb-2">
                <h6 class="news-title">📌 ${article.title}</h6>
                <p class="news-time"><i class="far fa-clock"></i> ${article.published}</p>
                <a href="${article.link}" target="_blank" class="news-link">
                    🔗 Đọc chi tiết →
                </a>
            </div>
        `;
    });

    return `
        <div class="card shadow-sm mb-3">
            <div class="card-header bg-gradient-pink text-white">
                <h5 class="mb-0">${source}</h5>
            </div>
            <div class="card-body">
                ${articlesHTML}
            </div>
        </div>
    `;
}

// ===========================
// Macro Data Functions
// ===========================

document.getElementById('loadMacroDataBtn').addEventListener('click', loadMacroData);

async function loadMacroData() {
    const macroLoading = document.getElementById('macroLoading');
    const macroContainer = document.getElementById('macroDataContainer');

    macroLoading.classList.remove('d-none');
    macroContainer.innerHTML = '';

    try {
        const response = await fetch(`${API_BASE}/api/macro-data`);
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || 'Lỗi khi tải dữ liệu vĩ mô');
        }

        const data = result.data;
        displayMacroData(data);

    } catch (error) {
        console.error('Error:', error);
        macroContainer.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle"></i> ${error.message}
            </div>
        `;
    } finally {
        macroLoading.classList.add('d-none');
    }
}

function displayMacroData(data) {
    const container = document.getElementById('macroDataContainer');

    let html = '<div class="row">';

    // GDP Growth
    if (data.gdp_growth) {
        html += `
            <div class="col-md-6 mb-3">
                <div class="card shadow-sm">
                    <div class="card-header bg-success text-white">
                        <h5 class="mb-0">📈 Tăng Trưởng GDP</h5>
                    </div>
                    <div class="card-body">
                        <canvas id="gdpChart"></canvas>
                    </div>
                </div>
            </div>
        `;
    }

    // Lending Rate vs Interbank
    if (data.lending_rate_vs_interbank) {
        html += `
            <div class="col-md-6 mb-3">
                <div class="card shadow-sm">
                    <div class="card-header bg-info text-white">
                        <h5 class="mb-0">💰 Lãi Suất Cho Vay vs Liên Ngân Hàng</h5>
                    </div>
                    <div class="card-body">
                        <canvas id="rateChart"></canvas>
                    </div>
                </div>
            </div>
        `;
    }

    // NPL Ratio
    if (data.npl_ratio) {
        html += `
            <div class="col-md-6 mb-3">
                <div class="card shadow-sm">
                    <div class="card-header bg-warning text-white">
                        <h5 class="mb-0">⚠️ Tỷ Lệ Nợ Xấu (NPL)</h5>
                    </div>
                    <div class="card-body">
                        <canvas id="nplChart"></canvas>
                    </div>
                </div>
            </div>
        `;
    }

    // Unemployment Rate
    if (data.unemployment_rate) {
        html += `
            <div class="col-md-6 mb-3">
                <div class="card shadow-sm">
                    <div class="card-header bg-secondary text-white">
                        <h5 class="mb-0">👥 Tỷ Lệ Thất Nghiệp</h5>
                    </div>
                    <div class="card-body">
                        <canvas id="unemploymentChart"></canvas>
                    </div>
                </div>
            </div>
        `;
    }

    html += '</div>';

    // Analysis
    if (data.analysis) {
        html += `
            <div class="card shadow-sm mt-3">
                <div class="card-header bg-gradient-pink text-white">
                    <h5 class="mb-0">📊 Phân Tích Tổng Quan</h5>
                </div>
                <div class="card-body">
                    <p class="mb-0">${data.analysis}</p>
                </div>
            </div>
        `;
    }

    container.innerHTML = html;

    // Create charts
    setTimeout(() => {
        if (data.gdp_growth) {
            createLineChart('gdpChart', data.gdp_growth.quarters, data.gdp_growth.growth_rate, 'Tăng trưởng GDP (%)', '#28a745');
        }
        if (data.lending_rate_vs_interbank) {
            createDualLineChart('rateChart', data.lending_rate_vs_interbank);
        }
        if (data.npl_ratio) {
            createLineChart('nplChart', data.npl_ratio.quarters, data.npl_ratio.npl_rate, 'NPL Ratio (%)', '#ffc107');
        }
        if (data.unemployment_rate) {
            createBarChart('unemploymentChart', data.unemployment_rate.years, data.unemployment_rate.rate, 'Tỷ lệ thất nghiệp (%)', '#6c757d');
        }
    }, 100);
}

// ===========================
// Industry Data Functions
// ===========================

document.getElementById('loadIndustryBtn').addEventListener('click', loadIndustryData);

async function loadIndustryData() {
    const industryName = document.getElementById('industrySelect').value;
    const industryLoading = document.getElementById('industryLoading');
    const industryContainer = document.getElementById('industryDataContainer');

    industryLoading.classList.remove('d-none');
    industryContainer.innerHTML = '';

    try {
        const response = await fetch(`${API_BASE}/api/industry-data`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ industry_name: industryName })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || 'Lỗi khi tải dữ liệu ngành');
        }

        const data = result.data;
        displayIndustryData(data);

    } catch (error) {
        console.error('Error:', error);
        industryContainer.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle"></i> ${error.message}
            </div>
        `;
    } finally {
        industryLoading.classList.add('d-none');
    }
}

function displayIndustryData(data) {
    const container = document.getElementById('industryDataContainer');

    let html = `
        <div class="row">
            <div class="col-12 mb-3">
                <div class="card shadow-sm">
                    <div class="card-header bg-gradient-pink text-white">
                        <h5 class="mb-0">🏢 Ngành: ${data.industry_name}</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-4">
                                <div class="stat-box">
                                    <h6>Biên Lợi Nhuận Gộp TB (3 năm)</h6>
                                    <h3>${data.avg_gross_margin_3y}%</h3>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="stat-box">
                                    <h6>Biên Lợi Nhuận Ròng TB</h6>
                                    <h3>${data.avg_net_profit_margin}%</h3>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="stat-box">
                                    <h6>Nợ/VCSH TB</h6>
                                    <h3>${data.avg_debt_to_equity}</h3>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Revenue Growth
    if (data.revenue_growth_quarterly) {
        html += `
            <div class="card shadow-sm mb-3">
                <div class="card-header bg-success text-white">
                    <h5 class="mb-0">📊 Tăng Trưởng Doanh Thu Theo Quý</h5>
                </div>
                <div class="card-body">
                    <canvas id="revenueGrowthChart"></canvas>
                </div>
            </div>
        `;
    }

    // PMI
    if (data.pmi_monthly) {
        html += `
            <div class="card shadow-sm mb-3">
                <div class="card-header bg-warning text-white">
                    <h5 class="mb-0">📈 PMI Theo Tháng</h5>
                </div>
                <div class="card-body">
                    <canvas id="pmiChart"></canvas>
                </div>
            </div>
        `;
    }

    // New vs Closed Businesses
    if (data.new_vs_closed_businesses) {
        html += `
            <div class="card shadow-sm mb-3">
                <div class="card-header bg-info text-white">
                    <h5 class="mb-0">🏢 DN Đăng Ký Mới vs Giải Thể</h5>
                </div>
                <div class="card-body">
                    <canvas id="businessChart"></canvas>
                </div>
            </div>
        `;
    }

    // Analysis
    if (data.analysis) {
        html += `
            <div class="card shadow-sm mt-3">
                <div class="card-header bg-gradient-pink text-white">
                    <h5 class="mb-0">💡 Phân Tích</h5>
                </div>
                <div class="card-body">
                    <p class="mb-0">${data.analysis}</p>
                </div>
            </div>
        `;
    }

    container.innerHTML = html;

    // Create charts
    setTimeout(() => {
        if (data.revenue_growth_quarterly) {
            createLineChart('revenueGrowthChart', data.revenue_growth_quarterly.quarters, data.revenue_growth_quarterly.growth_rate, 'Tăng trưởng (%)', '#28a745');
        }
        if (data.pmi_monthly) {
            createLineChart('pmiChart', data.pmi_monthly.months, data.pmi_monthly.pmi, 'PMI', '#ffc107');
        }
        if (data.new_vs_closed_businesses) {
            createDualBarChart('businessChart', data.new_vs_closed_businesses);
        }
    }, 100);
}

// ===========================
// Chart Helper Functions
// ===========================

function createLineChart(canvasId, labels, data, label, color) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                borderColor: color,
                backgroundColor: color + '33',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true
                }
            }
        }
    });
}

function createBarChart(canvasId, labels, data, label, color) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                backgroundColor: color,
                borderColor: color,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true
                }
            }
        }
    });
}

function createDualLineChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.quarters,
            datasets: [
                {
                    label: 'Lãi suất cho vay (%)',
                    data: data.lending_rate,
                    borderColor: '#dc3545',
                    backgroundColor: '#dc354533',
                    fill: false,
                    tension: 0.4
                },
                {
                    label: 'Lãi suất liên ngân hàng (%)',
                    data: data.interbank_rate,
                    borderColor: '#17a2b8',
                    backgroundColor: '#17a2b833',
                    fill: false,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true
                }
            }
        }
    });
}

function createDualBarChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.quarters,
            datasets: [
                {
                    label: 'DN Đăng ký mới',
                    data: data.new,
                    backgroundColor: '#28a745'
                },
                {
                    label: 'DN Giải thể',
                    data: data.closed,
                    backgroundColor: '#dc3545'
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true
                }
            }
        }
    });
}

console.log('Dashboard JavaScript Loaded');
