// Patient Report Dashboard JavaScript

const API_BASE = window.API_BASE || 'http://localhost:8000';
let currentUserId = 1;
let currentDate = null;
let autoRefreshInterval = null;
let radarChart = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializePage();
    setupEventListeners();
    loadLatestReport();
});

function initializePage() {
    // Default: no date selected, use latest record
    currentDate = null;
    document.getElementById('dateSelect').value = '';
    
    // Load user list
    loadUsers();
    
    // Enable auto-refresh by default
    setTimeout(() => {
        toggleAutoRefresh();
    }, 1000);
}

function setupEventListeners() {
    document.getElementById('refreshBtn').addEventListener('click', () => {
        loadReport();
    });
    
    document.getElementById('autoRefreshBtn').addEventListener('click', () => {
        toggleAutoRefresh();
    });
    
    document.getElementById('userSelect').addEventListener('change', (e) => {
        currentUserId = parseInt(e.target.value);
        loadReport();
    });
    
    document.getElementById('dateSelect').addEventListener('change', (e) => {
        const selectedDate = e.target.value;
        currentDate = selectedDate || null; // Convert empty string to null
        
        // If date is selected, stop auto-refresh
        if (selectedDate && autoRefreshInterval) {
            toggleAutoRefresh();
        }
        
        // If date selection is cleared, re-enable auto-refresh
        if (!selectedDate && !autoRefreshInterval) {
            toggleAutoRefresh();
        }
        
        loadReport();
    });
}

async function loadUsers() {
    try {
        const response = await fetch(`${API_BASE}/api/doctor/users`);
        const data = await response.json();
        
        if (data.success) {
            const select = document.getElementById('userSelect');
            select.innerHTML = '';
            data.users.forEach(user => {
                const option = document.createElement('option');
                option.value = user.id;
                option.textContent = `User ${user.id} - ${user.name || 'Unnamed'}`;
                select.appendChild(option);
            });
            currentUserId = data.users[0]?.id || 1;
        }
    } catch (error) {
        console.error('Failed to load user list:', error);
    }
}

async function loadLatestReport() {
    currentDate = null; // Use latest date
    await loadReport();
}

async function loadReport() {
    try {
        console.log(`🔄 Loading report - User ID: ${currentUserId}, Date: ${currentDate || 'Latest'}`);
        
        let analysis, date;
        
        if (currentDate) {
            // Get record for specified date
            const response = await fetch(`${API_BASE}/api/doctor/user/${currentUserId}/records?limit=50`);
            const data = await response.json();
            
            if (data.success) {
                const record = data.records?.find(r => r.date === currentDate);
                if (record) {
                    analysis = record.analysis_json;
                    date = record.date;
                    console.log(`✅ Found record for date: ${date}`);
                } else {
                    showError('No record found for the selected date');
                    return;
                }
            } else {
                showError('Failed to fetch records');
                return;
            }
        } else {
            // Get latest record
            const response = await fetch(`${API_BASE}/api/analysis/user/${currentUserId}/latest`);
            const data = await response.json();
            
            if (data.success) {
                analysis = data.analysis;
                date = data.date;
                console.log(`✅ Retrieved latest record: ${date}`, analysis);
            } else {
                showError('Failed to fetch latest record');
                return;
            }
        }
        
        if (analysis) {
            displayReport(analysis, date);
        } else {
            console.warn('⚠ Analysis data is empty');
            showError('Analysis data is empty');
        }
    } catch (error) {
        console.error('❌ Failed to load report:', error);
        showError('Failed to load report: ' + error.message);
    }
}

function displayReport(analysis, date) {
    // Update date display (show last update time)
    const now = new Date().toLocaleTimeString('en-US');
    document.getElementById('reportDate').textContent = `Report Date: ${date} | Last Updated: ${now}`;
    
    console.log('📊 Displaying report:', date, analysis); // Debug log
    
    // A. Risk Assessment
    displayRiskAssessment(analysis.risk_assessment);
    
    // B. Clinical Scores
    displayClinicalScores(analysis.clinical_scores);
    
    // C. Cognitive Distortions
    displayCognitiveDistortions(analysis.cognitive_distortions || []);
    
    // D. Presenting Problem & Situation
    displayProblemAndSituation(analysis.presenting_problem, analysis.situation_description);
    
    // E. Emotions & Physical Reactions
    displayEmotionsAndPhysical(analysis.emotions || [], analysis.physical_reactions || []);
    
    // F. Automatic Thoughts
    displayAutomaticThoughts(analysis.automatic_thoughts || []);
    
    // G. Behaviors & Consequences
    displayBehaviorsAndConsequences(analysis.behavior_reactions || [], analysis.consequences);
    
    // H. Desired Change
    displayDesiredChange(analysis.desired_change);
    
    // I. Profile Update
    displayProfileUpdate(analysis.profile_update);
}

function displayRiskAssessment(risk) {
    const section = document.getElementById('riskSection');
    const content = document.getElementById('riskContent');
    
    const riskLevel = risk.self_harm_risk_0_3 || 0;
    const crisisFlag = risk.crisis_flag || false;
    
    // Set card style
    section.className = 'card risk-card';
    if (riskLevel === 0) {
        section.classList.add('low-risk');
    } else if (riskLevel <= 2) {
        section.classList.add('medium-risk');
    } else {
        section.classList.add('high-risk');
    }
    
    const riskLabels = ['No Risk', 'Low Risk', 'Medium Risk', 'High Risk'];
    const riskColors = ['low', 'low', 'medium', 'high'];
    
    content.innerHTML = `
        <div class="risk-level ${riskColors[riskLevel]}">
            Self-harm Risk Level: ${riskLabels[riskLevel]} (${riskLevel}/3)
        </div>
        <div class="crisis-flag ${crisisFlag}">
            Crisis Flag: ${crisisFlag ? 'TRUE ⚠️' : 'FALSE'}
        </div>
        ${crisisFlag ? '<p style="margin-top: 15px; color: #c0392b; font-weight: bold;">⚠️ Immediate attention required! Patient may be in crisis.</p>' : ''}
    `;
}

function displayClinicalScores(scores) {
    const scoreData = {
        anxiety: scores.anxiety_0_10 || 0,
        depression: scores.depression_0_10 || 0,
        stress: scores.stress_0_10 || 0,
        rumination: scores.rumination_0_10 || 0,
        avoidance: scores.avoidance_0_10 || 0,
        self_blame: scores.self_blame_0_10 || 0
    };
    
    // Create radar chart
    const ctx = document.getElementById('radarChart').getContext('2d');
    
    if (radarChart) {
        radarChart.destroy();
    }
    
    radarChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Anxiety', 'Depression', 'Stress', 'Rumination', 'Avoidance', 'Self-blame'],
            datasets: [{
                label: 'Clinical Scores',
                data: [
                    scoreData.anxiety,
                    scoreData.depression,
                    scoreData.stress,
                    scoreData.rumination,
                    scoreData.avoidance,
                    scoreData.self_blame
                ],
                backgroundColor: 'rgba(52, 152, 219, 0.2)',
                borderColor: 'rgba(52, 152, 219, 1)',
                pointBackgroundColor: 'rgba(52, 152, 219, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(52, 152, 219, 1)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 10,
                    ticks: {
                        stepSize: 2
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
    
    // Create bar chart
    const barsContainer = document.getElementById('scoreBars');
    const labels = {
        anxiety: 'Anxiety',
        depression: 'Depression',
        stress: 'Stress',
        rumination: 'Rumination',
        avoidance: 'Avoidance',
        self_blame: 'Self-blame'
    };
    
    barsContainer.innerHTML = Object.entries(scoreData).map(([key, value]) => `
        <div class="score-bar">
            <div class="score-bar-label">
                <span>${labels[key]}</span>
                <span>${value}/10</span>
            </div>
            <div class="score-bar-fill" style="width: ${(value / 10) * 100}%">
                ${value}
            </div>
        </div>
    `).join('');
}

function displayCognitiveDistortions(distortions) {
    const container = document.getElementById('distortionsContent');
    
    if (!distortions || distortions.length === 0) {
        container.innerHTML = '<div class="empty-state">None detected.</div>';
        return;
    }
    
    const distortionLabels = {
        'all-or-nothing thinking': 'All-or-nothing Thinking',
        'catastrophizing': 'Catastrophizing',
        'overgeneralization': 'Overgeneralization',
        'emotional reasoning': 'Emotional Reasoning',
        'mind reading': 'Mind Reading',
        'fortune telling': 'Fortune Telling',
        'should statements': 'Should Statements',
        'personalization': 'Personalization',
        'self-blame': 'Self-blame',
        'labeling': 'Labeling',
        'discounting the positive': 'Discounting the Positive'
    };
    
    container.innerHTML = distortions.map(distortion => {
        const className = distortion.toLowerCase().replace(/\s+/g, '-').replace(/[()]/g, '');
        return `<span class="distortion-tag ${className}">${distortionLabels[distortion] || distortion}</span>`;
    }).join('');
}

function displayProblemAndSituation(problem, situation) {
    const container = document.getElementById('problemContent');
    
    container.innerHTML = `
        <div style="margin-bottom: 20px;">
            <h3 style="color: #2c3e50; margin-bottom: 10px;">Presenting Problem</h3>
            <div style="padding: 15px; background: #f8f9fa; border-radius: 6px; border-left: 4px solid #3498db;">
                ${problem || '<em>Not mentioned</em>'}
            </div>
        </div>
        <div>
            <h3 style="color: #2c3e50; margin-bottom: 10px;">Situation Summary</h3>
            <div class="situation-grid">
                <div class="situation-item">
                    <strong>When</strong>
                    <span>${situation?.when || 'Not mentioned'}</span>
                </div>
                <div class="situation-item">
                    <strong>Where</strong>
                    <span>${situation?.where || 'Not mentioned'}</span>
                </div>
                <div class="situation-item">
                    <strong>Who</strong>
                    <span>${situation?.who || 'Not mentioned'}</span>
                </div>
                <div class="situation-item">
                    <strong>What Happened</strong>
                    <span>${situation?.what_happened || 'Not mentioned'}</span>
                </div>
            </div>
        </div>
    `;
}

function displayEmotionsAndPhysical(emotions, physical) {
    const container = document.getElementById('emotionsContent');
    
    let html = '<div style="margin-bottom: 20px;"><h3 style="color: #2c3e50; margin-bottom: 15px;">Emotions</h3>';
    
    if (emotions.length === 0) {
        html += '<div class="empty-state">Not mentioned</div>';
    } else {
        emotions.forEach(emotion => {
            const intensity = emotion.intensity_0_100 || 0;
            html += `
                <div class="emotion-item">
                    <div class="emotion-label">${emotion.type || 'Unknown'}</div>
                    <div class="emotion-intensity">
                        <div class="intensity-bar" style="width: ${intensity}%">
                            ${intensity >= 30 ? intensity : ''}
                        </div>
                    </div>
                    <div class="intensity-value">${intensity}/100</div>
                </div>
            `;
        });
    }
    
    html += '</div>';
    
    if (physical.length > 0) {
        html += `
            <div class="physical-reactions">
                <h3>Physical Reactions</h3>
                ${physical.map(reaction => `<span class="physical-tag">${reaction}</span>`).join('')}
            </div>
        `;
    }
    
    container.innerHTML = html;
}

function displayAutomaticThoughts(thoughts) {
    const container = document.getElementById('thoughtsContent');
    
    if (thoughts.length === 0) {
        container.innerHTML = '<div class="empty-state">Not mentioned</div>';
        return;
    }
    
    container.innerHTML = thoughts.map(thought => `
        <div class="thought-card">"${thought}"</div>
    `).join('');
}

function displayBehaviorsAndConsequences(behaviors, consequences) {
    const container = document.getElementById('behaviorsContent');
    
    let html = '<div class="behavior-section">';
    html += '<h3>Behavior Reactions</h3>';
    
    if (behaviors.length === 0) {
        html += '<div class="empty-state">Not mentioned</div>';
    } else {
        html += behaviors.map(behavior => `
            <div class="behavior-item">• ${behavior}</div>
        `).join('');
    }
    
    html += '</div>';
    
    if (consequences) {
        html += `
            <div class="behavior-section">
                <h3>Consequences</h3>
                <div class="consequences-text">${consequences}</div>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

function displayDesiredChange(desiredChange) {
    const container = document.getElementById('desiredChangeContent');
    
    if (!desiredChange) {
        container.innerHTML = '<div class="empty-state">Not mentioned</div>';
        return;
    }
    
    container.innerHTML = `<div class="desired-change-text">"${desiredChange}"</div>`;
}

function displayProfileUpdate(profile) {
    const container = document.getElementById('profileUpdateContent');
    
    const trendNotes = profile?.trend_notes || '';
    const suggestions = profile?.suggestions_to_therapist || '';
    
    let html = '';
    
    if (trendNotes) {
        html += `
            <div class="profile-section">
                <h3>Trend Notes</h3>
                <div class="trend-notes">${trendNotes}</div>
            </div>
        `;
    }
    
    if (suggestions) {
        html += `
            <div class="profile-section">
                <h3>Suggestions to Therapist</h3>
                <div class="suggestions">${suggestions}</div>
            </div>
        `;
    }
    
    if (!html) {
        html = '<div class="empty-state">No updates</div>';
    }
    
    container.innerHTML = html;
}

function toggleAutoRefresh() {
    const btn = document.getElementById('autoRefreshBtn');
    
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
        btn.textContent = 'Auto Refresh: Off';
        btn.classList.remove('active');
    } else {
        // If a specific date is selected, don't auto-refresh (because historical records won't change)
        if (currentDate) {
            alert('A specific date is selected. Auto-refresh is disabled. Please clear the date selection to enable auto-refresh.');
            return;
        }
        
        autoRefreshInterval = setInterval(() => {
            // Only auto-refresh when viewing latest records
            if (!currentDate) {
                loadReport();
            }
        }, 3000); // Refresh every 3 seconds
        btn.textContent = 'Auto Refresh: On (3s)';
        btn.classList.add('active');
    }
}

function showError(message) {
    const container = document.querySelector('.container');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'card';
    errorDiv.style.background = '#fee';
    errorDiv.style.borderLeft = '4px solid #e74c3c';
    errorDiv.innerHTML = `<h2 style="color: #e74c3c;">Error</h2><p>${message}</p>`;
    container.insertBefore(errorDiv, container.firstChild);
    
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

