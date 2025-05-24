const app = document.querySelector('.weather-app');
const temp = document.querySelector('.temp');
const dateOutput = document.querySelector('.date');
const timeOutput = document.querySelector('.time');
const conditionOutput = document.querySelector('.condition');
const nameOutput = document.querySelector('.name');
const icon = document.querySelector('.icon');
const cloudOutput = document.querySelector('.cloud');
const humidityOutput = document.querySelector('.humidity');
const windOutput = document.querySelector('.wind');
const form = document.getElementById('locationInput');
const search = document.querySelector('.search');
const btn = document.querySelector('.submit');
const cities = document.querySelectorAll('.city');

// AI UI Elements
const aiInsights = document.getElementById('aiInsights');
const insightsContent = document.getElementById('insightsContent');
const aiStatus = document.getElementById('aiStatus');
const chatContainer = document.getElementById('chatContainer');
const chatMessages = document.getElementById('chatMessages');
const chatForm = document.getElementById('chatForm');
const chatInput = document.getElementById('chatInput');
const chatToggle = document.getElementById('chatToggle');

// API base URL - FastAPI server
const API_BASE_URL = 'http://localhost:8000/api';

// Default city when the page loads
let cityInput = "Nairobi";

// Enhanced global state
let currentWeatherData = null;
let lastUpdateTime = null;
let isAIAvailable = false;
let chatOpen = true;

// Add click event to each city in the panel
cities.forEach((city) => {
    city.addEventListener('click', (e) => {
        cityInput = e.target.innerHTML;
        fetchWeatherData();
        app.style.opacity = "0";
    });
});

// Add submit event to the form with improved validation
form.addEventListener('submit', (e) => {
    const searchValue = search.value.trim();
    
    if(searchValue.length == 0) {
        alert('Please type in a city name');
    } else if(searchValue.length < 2) {
        alert('Please enter at least 2 characters');
    } else {
        cityInput = searchValue;
        fetchWeatherData();
        search.value = "";
        app.style.opacity = "0";
    }
    
    e.preventDefault();
});

// Chat toggle functionality
chatToggle.addEventListener('click', () => {
    chatOpen = !chatOpen;
    chatContainer.classList.toggle('collapsed', !chatOpen);
    const icon = chatToggle.querySelector('i');
    icon.className = chatOpen ? 'fas fa-chevron-up' : 'fas fa-chevron-down';
});

// Chat form submission
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = chatInput.value.trim();
    if (message) {
        await sendChatMessage(message);
        chatInput.value = '';
    }
});

// Enhanced date parsing function that handles edge cases
function dayOfTheWeek(day, month, year) {
    const weekday = [
        "Sunday", "Monday", "Tuesday", "Wednesday", 
        "Thursday", "Friday", "Saturday"
    ];
    
    try {
        const date = new Date(year, month - 1, day);
        return weekday[date.getDay()];
    } catch (error) {
        console.warn('Date parsing error:', error);
        return "Unknown";
    }
}

// Enhanced function that fetches and displays the data from our FastAPI backend
async function fetchWeatherData() {
    try {
        console.log(`🌤️ Fetching weather data for: ${cityInput}`);
        
        // Enhanced loading state with spinner
        temp.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        conditionOutput.innerHTML = "Loading weather...";
        nameOutput.innerHTML = "Searching...";
        updateInsightsLoading();
        
        const response = await fetch(`${API_BASE_URL}/weather/simple/${encodeURIComponent(cityInput)}`);
        
        console.log(`Response status: ${response.status}`);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: "Unknown error" }));
            throw new Error(`HTTP ${response.status}: ${errorData.detail || response.statusText}`);
        }
        
        const data = await response.json();
        console.log('📊 Weather data received:', data);
        
        // Store current data for potential future use
        currentWeatherData = data;
        lastUpdateTime = new Date();
        
        // Validate data structure
        if (!data.current || !data.location) {
            throw new Error("Invalid weather data format received");
        }
        
        // Enhanced temperature display with rounding
        temp.innerHTML = Math.round(data.current.temp_c) + "&#176;";
        conditionOutput.innerHTML = data.current.condition.text;
        
        // Enhanced date and time parsing
        const date = data.location.localtime;
        
        try {
            const y = parseInt(date.substr(0, 4));
            const m = parseInt(date.substr(5, 2));
            const d = parseInt(date.substr(8, 2));
            const time = date.substr(11) || "00:00";
            
            const dayName = dayOfTheWeek(d, m, y);
            dateOutput.innerHTML = `${dayName} ${d}/${m}/${y}`;
            timeOutput.innerHTML = time;
            
        } catch (dateError) {
            console.warn('Date parsing failed, using current date:', dateError);
            const now = new Date();
            dateOutput.innerHTML = now.toLocaleDateString();
            timeOutput.innerHTML = now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        }
        
        nameOutput.innerHTML = data.location.name;
        
        // FIXED ICON HANDLING - Use correct day/night paths
        const timeOfDay = data.current.is_day ? "day" : "night";
        const iconUrl = data.current.condition.icon;
        
        if (iconUrl.includes("cdn.weatherapi.com")) {
            const iconId = iconUrl.split("/").pop();
            icon.src = `./icons/${timeOfDay}/${iconId}`;
            
            icon.onerror = () => {
                console.warn(`Icon not found: ./icons/${timeOfDay}/${iconId}, trying fallback`);
                const fallbackTime = timeOfDay === "day" ? "night" : "day";
                icon.src = `./icons/${fallbackTime}/${iconId}`;
                
                icon.onerror = () => {
                    console.warn("Using default icon");
                    icon.src = "./icons/day/113.png";
                    icon.onerror = null;
                };
            };
        } else {
            icon.src = `./icons/${timeOfDay}/113.png`;
        }
        
        // Enhanced weather details with better formatting
        cloudOutput.innerHTML = Math.round(data.current.cloud) + "%";
        humidityOutput.innerHTML = Math.round(data.current.humidity) + "%";
        windOutput.innerHTML = Math.round(data.current.wind_kph) + "km/h";
        
        const code = data.current.condition.code; 
        updateAppTheme(code, timeOfDay);
        
        // Display enhanced analysis in UI
        if (data.analysis) {
            displayWeatherInsightsUI(data.analysis);
        } else {
            updateInsightsContent("No detailed analysis available for this location.");
        }
        
        app.style.opacity = "1";
        console.log("✅ Weather data updated successfully");
        
    } catch (error) {
        console.error('❌ Error fetching weather data:', error);
        handleWeatherError(error);
    }
}

// New function to update insights loading state
function updateInsightsLoading() {
    insightsContent.innerHTML = '<p class="loading-insights">🔄 Analyzing weather data...</p>';
}

// New function to display weather insights in the UI
function displayWeatherInsightsUI(analysis) {
    let html = '';
    
    // Comfort Level
    if (analysis.comfort_level) {
        html += `
            <div class="insight-item comfort">
                <div class="insight-title">🌡️ Comfort Level</div>
                <div>${analysis.comfort_level}</div>
            </div>
        `;
    }
    
    // Recommendations
    if (analysis.recommendations && analysis.recommendations.length > 0) {
        html += `
            <div class="insight-item recommendation">
                <div class="insight-title">💡 Recommendations</div>
                <ul class="insight-list">
                    ${analysis.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    // Activities
    if (analysis.activities && analysis.activities.length > 0) {
        html += `
            <div class="insight-item activity">
                <div class="insight-title">🎯 Suggested Activities</div>
                <ul class="insight-list">
                    ${analysis.activities.map(activity => `<li>${activity}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    // Alerts
    if (analysis.alerts && analysis.alerts.length > 0) {
        html += `
            <div class="insight-item alert">
                <div class="insight-title">⚠️ Weather Alerts</div>
                <ul class="insight-list">
                    ${analysis.alerts.map(alert => `<li>${alert}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    // Air Quality
    if (analysis.air_quality && analysis.air_quality.level) {
        html += `
            <div class="insight-item air-quality">
                <div class="insight-title">🌬️ Air Quality</div>
                <div>${analysis.air_quality.level} - ${analysis.air_quality.advice}</div>
            </div>
        `;
    }
    
    insightsContent.innerHTML = html || '<p class="loading-insights">No detailed insights available.</p>';
}

// New function to update insights content
function updateInsightsContent(content) {
    insightsContent.innerHTML = `<p class="loading-insights">${content}</p>`;
}

// New function to send chat messages
async function sendChatMessage(message) {
    // Add user message to chat
    addMessageToChat(message, 'user');
    
    // Add typing indicator
    addTypingIndicator();
    
    try {
        const response = await chatWithAddy(message, cityInput);
        
        // Remove typing indicator
        removeTypingIndicator();
        
        if (response.status === 'success') {
            // Add AI response to chat
            addMessageToChat(response.response, 'ai');
            
            // Update AI status indicator
            aiStatus.textContent = response.ai_powered ? '🤖 AI' : '⚡ Enhanced';
            aiStatus.title = response.ai_powered ? 'Full AI Powered' : 'Enhanced Analysis';
        } else {
            addMessageToChat('Sorry, I encountered an error. Please try again.', 'ai');
        }
    } catch (error) {
        removeTypingIndicator();
        addMessageToChat('Sorry, I\'m having trouble connecting. Please try again.', 'ai');
        console.error('Chat error:', error);
    }
}

// New function to add messages to chat
function addMessageToChat(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const now = new Date();
    const timeStr = now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    
    messageDiv.innerHTML = `
        <div class="message-avatar">${sender === 'ai' ? '🤖' : '👤'}</div>
        <div class="message-content">
            <span class="message-text">${text}</span>
            <span class="message-time">${timeStr}</span>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// New function to add typing indicator
function addTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message ai-message typing-indicator-message';
    typingDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;
    
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// New function to remove typing indicator
function removeTypingIndicator() {
    const typingIndicator = chatMessages.querySelector('.typing-indicator-message');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Enhanced error handling function
function handleWeatherError(error) {
    temp.innerHTML = "N/A";
    conditionOutput.innerHTML = "Unable to load weather data";
    nameOutput.innerHTML = cityInput;
    
    const now = new Date();
    dateOutput.innerHTML = now.toLocaleDateString();
    timeOutput.innerHTML = now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    
    let errorMsg = `Unable to fetch weather data for "${cityInput}".`;
    
    if (error.message.includes('Network')) {
        errorMsg += ' Please check your internet connection.';
    } else if (error.message.includes('404')) {
        errorMsg += ' City not found. Please check the spelling.';
    } else if (error.message.includes('key')) {
        errorMsg = 'Weather service temporarily unavailable.';
    } else {
        errorMsg += ' Please try again later.';
    }
    
    updateInsightsContent(`❌ ${errorMsg}`);
    alert(errorMsg);
    app.style.opacity = "1";
}

// Keep your existing updateAppTheme function exactly as is
function updateAppTheme(code, timeOfDay) {
    if(code == 1000) { 
        app.style.backgroundImage = `url(./images/${timeOfDay}/clear.jpg)`;
        btn.style.background = "#e5ba92";
        if(timeOfDay == "night") {
            btn.style.background = "#181e27";
        }
    }
    else if (
        code == 1003 || code == 1006 || code == 1009 || code == 1030 ||
        code == 1069 || code == 1087 || code == 1135 || code == 1273 ||
        code == 1276 || code == 1279 || code == 1282
    ) {
        app.style.backgroundImage = `url(./images/${timeOfDay}/cloudy.jpg)`;
        btn.style.background = "#fa6d1b";
        if(timeOfDay == "night") {
            btn.style.background = "#181e27";
        }
    }
    else if (
        code == 1063 || code == 1069 || code == 1072 || code == 1150 ||
        code == 1153 || code == 1180 || code == 1183 || code == 1186 ||
        code == 1189 || code == 1192 || code == 1195 || code == 1204 ||
        code == 1207 || code == 1240 || code == 1243 || code == 1246 ||
        code == 1249 || code == 1252 
    ) {
        app.style.backgroundImage = `url(./images/${timeOfDay}/rainy.jpg)`;
        btn.style.background = "#647d75";
        if(timeOfDay == "night") {
            btn.style.background = "#325c80";
        }
    }
    else {
        app.style.backgroundImage = `url(./images/${timeOfDay}/snowy.jpg)`;
        btn.style.background = "#4d72aa";
        if(timeOfDay == "night") {
            btn.style.background = "#1b1b1b";
        }
    }
}

// Enhanced chat with Addy agent function
async function chatWithAddy(message, location = null) {
    try {
        console.log(`💬 Chatting with Addy: "${message}"`);
        
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                location: location || cityInput
            })
        });
        
        if (!response.ok) {
            throw new Error(`Chat service error: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('🤖 Addy response:', data);
        
        return data;
        
    } catch (error) {
        console.error('💥 Error chatting with Addy:', error);
        return {
            status: "error",
            error_message: "Failed to communicate with Addy agent"
        };
    }
}

// Enhanced initialization with AI status check
async function initializeApp() {
    console.log("🚀 Initializing Addy Weather Monitor v3.0...");
    
    try {
        const healthResponse = await Promise.race([
            fetch(`${API_BASE_URL}/health`),
            new Promise((_, reject) => 
                setTimeout(() => reject(new Error('Health check timeout')), 5000)
            )
        ]);
        
        const healthData = await healthResponse.json();
        console.log("✅ API Health Check:", healthData);
        
        // Update AI status in UI
        isAIAvailable = healthData.ai_available;
        aiStatus.textContent = isAIAvailable ? '🤖 AI' : '⚡ Enhanced';
        aiStatus.title = isAIAvailable ? 'Full AI Powered' : 'Enhanced Analysis';
        
        if (healthData.app_name) {
            console.log(`📱 ${healthData.app_name} v${healthData.version || '3.0'}`);
            console.log(`🤖 AI Mode: ${healthData.ai_mode}`);
            
            if (healthData.ai_available) {
                console.log("🧠 Full AI capabilities active!");
                addMessageToChat("Hi! I'm Addy with full AI capabilities. Ask me anything about weather!", 'ai');
            } else if (healthData.enhanced_analysis) {
                console.log("⚡ Enhanced analysis available");
                addMessageToChat("Hi! I'm Addy with enhanced weather analysis. How can I help you?", 'ai');
            } else {
                addMessageToChat("Hi! I'm Addy in basic mode. I can help with weather data!", 'ai');
            }
        }
        
    } catch (error) {
        console.warn("⚠️ API health check failed:", error.message);
        aiStatus.textContent = '❌ Offline';
        aiStatus.title = 'Service unavailable';
        addMessageToChat("I'm having trouble connecting to my AI services, but I can still help with basic weather data!", 'ai');
    }
    
    // Load initial weather data
    fetchWeatherData();
    
    // Set up periodic refresh (every 10 minutes)
    setInterval(() => {
        console.log("🔄 Auto-refreshing weather data...");
        fetchWeatherData();
    }, 600000);
    
    console.log("⏰ Auto-refresh enabled (every 10 minutes)");
}

// Enhanced keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if ((e.key === 'r' || e.key === 'R') && !e.ctrlKey && !e.altKey && !e.metaKey) {
        console.log("🔄 Manual refresh triggered via keyboard");
        fetchWeatherData();
    }
    
    if ((e.key === 'c' || e.key === 'C') && !e.ctrlKey && !e.altKey && !e.metaKey) {
        if (currentWeatherData) {
            console.log("📊 Current Weather Data:", currentWeatherData);
            console.log(`🕐 Last Updated: ${lastUpdateTime.toLocaleString()}`);
        } else {
            console.log("❌ No weather data available");
        }
    }
    
    if ((e.key === 'a' || e.key === 'A') && !e.ctrlKey && !e.altKey && !e.metaKey) {
        if (!chatOpen) {
            chatToggle.click();
        }
        chatInput.focus();
    }
});

// Enhanced utility functions for debugging
window.addyWeather = {
    fetchWeatherData,
    chatWithAddy,
    updateAppTheme,
    currentCity: () => cityInput,
    getCurrentData: () => currentWeatherData,
    getLastUpdate: () => lastUpdateTime,
    setCity: (city) => {
        cityInput = city;
        fetchWeatherData();
    },
    testChat: (message) => sendChatMessage(message),
    refreshNow: () => fetchWeatherData(),
    checkAI: async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/ai-status`);
            const data = await response.json();
            console.log("🤖 AI Status:", data);
            return data;
        } catch (error) {
            console.error("❌ AI check failed:", error);
            return null;
        }
    },
    checkHealth: async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/health`);
            const data = await response.json();
            console.log("🏥 Health Check:", data);
            return data;
        } catch (error) {
            console.error("❌ Health check failed:", error);
            return null;
        }
    }
};

// Call the initialization function on page load
document.addEventListener('DOMContentLoaded', initializeApp);

console.log("🛠️ Developer Tools Available:");
console.log("   addyWeather.setCity('London') - Change city");
console.log("   addyWeather.refreshNow() - Manual refresh");
console.log("   addyWeather.testChat('Hello') - Test AI chat");
console.log("   addyWeather.checkAI() - Check AI status");
console.log("   addyWeather.checkHealth() - API health check");
console.log("🎹 Keyboard Shortcuts:");
console.log("   R - Refresh weather");
console.log("   C - Show current data");
console.log("   A - Open chat and focus input");