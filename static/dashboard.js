// Telnyx Patient Intake Agent - Dashboard JavaScript

// Configuration
const API_BASE_URL = window.location.origin;
const POLL_INTERVAL = 5000; // 5 seconds

// State
let currentCall = null;
let pollTimer = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initialized');
    loadStats();
    loadRecentCalls();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Call initiation form
    const callForm = document.getElementById('call-form');
    if (callForm) {
        callForm.addEventListener('submit', handleCallSubmit);
    }
    
    // Refresh buttons
    const refreshBtns = document.querySelectorAll('.btn-refresh');
    refreshBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            loadStats();
            loadRecentCalls();
        });
    });
}

// Handle call submission
async function handleCallSubmit(event) {
    event.preventDefault();
    
    const phoneInput = document.getElementById('phone-number');
    const phoneNumber = phoneInput.value.trim();
    
    if (!phoneNumber) {
        showAlert('Please enter a phone number', 'error');
        return;
    }
    
    // Validate E.164 format
    if (!phoneNumber.match(/^\+[1-9]\d{1,14}$/)) {
        showAlert('Phone number must be in E.164 format (e.g., +12345678900)', 'error');
        return;
    }
    
    try {
        showLoading('Initiating call...');
        
        const response = await fetch(`${API_BASE_URL}/api/calls`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                phone_number: phoneNumber
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert('Call initiated successfully!', 'success');
            phoneInput.value = '';
            
            // Start monitoring the call
            currentCall = data.call;
            startCallMonitoring(currentCall.id);
            
            // Refresh call list
            loadRecentCalls();
        } else {
            showAlert(`Failed to initiate call: ${data.error || 'Unknown error'}`, 'error');
        }
    } catch (error) {
        console.error('Error initiating call:', error);
        showAlert('Error initiating call. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

// Load statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/stats`);
        const data = await response.json();
        
        if (response.ok) {
            updateStatsDisplay(data);
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Update stats display
function updateStatsDisplay(data) {
    const totalCallsEl = document.getElementById('total-calls');
    const activeCallsEl = document.getElementById('active-calls');
    const completedCallsEl = document.getElementById('completed-calls');
    const totalPatientsEl = document.getElementById('total-patients');
    
    if (totalCallsEl) totalCallsEl.textContent = data.total_calls || 0;
    if (activeCallsEl) activeCallsEl.textContent = data.active_calls || 0;
    if (completedCallsEl) completedCallsEl.textContent = data.completed_calls || 0;
    if (totalPatientsEl) totalPatientsEl.textContent = data.total_patients || 0;
}

// Load recent calls
async function loadRecentCalls() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/calls?limit=10`);
        const data = await response.json();
        
        if (response.ok) {
            displayRecentCalls(data.calls || []);
        }
    } catch (error) {
        console.error('Error loading recent calls:', error);
    }
}

// Display recent calls
function displayRecentCalls(calls) {
    const tableBody = document.getElementById('recent-calls-body');
    if (!tableBody) return;
    
    if (calls.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="5" style="text-align: center;">No calls yet</td></tr>';
        return;
    }
    
    tableBody.innerHTML = calls.map(call => `
        <tr>
            <td>${call.id}</td>
            <td>${call.to_number || 'N/A'}</td>
            <td><span class="status-badge status-${call.status.toLowerCase().replace('_', '-')}">${call.status}</span></td>
            <td>${call.duration || 0}s</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="viewCallDetails(${call.id})">View</button>
            </td>
        </tr>
    `).join('');
}

// View call details
function viewCallDetails(callId) {
    window.location.href = `/calls/${callId}`;
}

// Start call monitoring
function startCallMonitoring(callId) {
    if (pollTimer) {
        clearInterval(pollTimer);
    }
    
    console.log(`Starting monitoring for call ${callId}`);
    
    pollTimer = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/calls/${callId}`);
            const data = await response.json();
            
            if (response.ok && data.call) {
                updateCallMonitor(data.call);
                
                // Stop polling if call is completed
                if (data.call.status === 'completed' || data.call.status === 'failed') {
                    stopCallMonitoring();
                }
            }
        } catch (error) {
            console.error('Error polling call status:', error);
        }
    }, POLL_INTERVAL);
}

// Stop call monitoring
function stopCallMonitoring() {
    if (pollTimer) {
        clearInterval(pollTimer);
        pollTimer = null;
    }
    console.log('Stopped call monitoring');
}

// Update call monitor display
function updateCallMonitor(call) {
    const monitorEl = document.getElementById('call-monitor');
    if (!monitorEl) return;
    
    monitorEl.innerHTML = `
        <div class="card">
            <div class="card-header">Active Call Monitor</div>
            <div style="padding: 10px 0;">
                <p><strong>Call ID:</strong> ${call.id}</p>
                <p><strong>Phone:</strong> ${call.to_number}</p>
                <p><strong>Status:</strong> <span class="status-badge status-${call.status.toLowerCase()}">${call.status}</span></p>
                <p><strong>Duration:</strong> ${call.duration || 0}s</p>
            </div>
        </div>
    `;
}

// Load transcripts for a call
async function loadTranscripts(callId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/calls/${callId}/transcripts`);
        const data = await response.json();
        
        if (response.ok) {
            displayTranscripts(data.transcripts || []);
        }
    } catch (error) {
        console.error('Error loading transcripts:', error);
    }
}

// Display transcripts
function displayTranscripts(transcripts) {
    const container = document.getElementById('transcript-container');
    if (!container) return;
    
    if (transcripts.length === 0) {
        container.innerHTML = '<p>No transcripts available yet.</p>';
        return;
    }
    
    container.innerHTML = transcripts.map(t => `
        <div class="transcript-item">
            <div class="transcript-time">${new Date(t.created_at).toLocaleString()}</div>
            <div class="transcript-text">${escapeHtml(t.text)}</div>
        </div>
    `).join('');
}

// Utility: Show alert
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container') || createAlertContainer();
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    
    alertContainer.appendChild(alert);
    
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

// Utility: Create alert container
function createAlertContainer() {
    const container = document.createElement('div');
    container.id = 'alert-container';
    container.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
    document.body.appendChild(container);
    return container;
}

// Utility: Show loading
function showLoading(message = 'Loading...') {
    const loader = document.getElementById('loader') || createLoader();
    loader.querySelector('.loading-message').textContent = message;
    loader.style.display = 'flex';
}

// Utility: Hide loading
function hideLoading() {
    const loader = document.getElementById('loader');
    if (loader) {
        loader.style.display = 'none';
    }
}

// Utility: Create loader
function createLoader() {
    const loader = document.createElement('div');
    loader.id = 'loader';
    loader.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: none; align-items: center; justify-content: center; z-index: 10000;';
    loader.innerHTML = `
        <div style="background: white; padding: 30px; border-radius: 8px; text-align: center;">
            <div class="spinner"></div>
            <p class="loading-message" style="margin-top: 15px;">Loading...</p>
        </div>
    `;
    document.body.appendChild(loader);
    return loader;
}

// Utility: Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Export for use in other scripts
window.DashboardAPI = {
    loadStats,
    loadRecentCalls,
    loadTranscripts,
    startCallMonitoring,
    stopCallMonitoring,
    showAlert
};
