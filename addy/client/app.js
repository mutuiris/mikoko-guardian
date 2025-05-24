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

// API base URL - FastAPI server
const API_BASE_URL = 'http://localhost:8000/api';

// Default city when the page loads
let cityInput = "Nairobi";

// Enhanced global state
let currentWeatherData = null;
let lastUpdateTime = null;

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

// Enhanced date parsing function that handles edge cases
function dayOfTheWeek(day, month, year) {
    const weekday = [
        "Sunday", "Monday", "Tuesday", "Wednesday", 
        "Thursday", "Friday", "Saturday"
    ];
    
    try {
        // Handle different date formats more robustly
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
            
            // Enhanced date formatting with better error handling
            const dayName = dayOfTheWeek(d, m, y);
            dateOutput.innerHTML = `${dayName} ${d}/${m}/${y}`;
            timeOutput.innerHTML = time;
            
        } catch (dateError) {
            console.warn('Date parsing failed, using current date:', dateError);
            const now = new Date();
            dateOutput.innerHTML = now.toLocaleDateString();
            timeOutput.innerHTML = now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        }
        
        // Add the name of the city
        nameOutput.innerHTML = data.location.name;
        
        // FIXED ICON HANDLING - Use correct day/night paths
        const timeOfDay = data.current.is_day ? "day" : "night";
        const iconUrl = data.current.condition.icon;
        
        if (iconUrl.includes("cdn.weatherapi.com")) {
            // Extract icon filename from WeatherAPI URL
            const iconId = iconUrl.split("/").pop();
            // Use the correct day/night path structure
            icon.src = `./icons/${timeOfDay}/${iconId}`;
            
            // Add error handler for missing icons
            icon.onerror = () => {
                console.warn(`Icon not found: ./icons/${timeOfDay}/${iconId}, trying fallback`);
                // Try opposite time of day
                const fallbackTime = timeOfDay === "day" ? "night" : "day";
                icon.src = `./icons/${fallbackTime}/${iconId}`;
                
                // If that fails too, use default
                icon.onerror = () => {
                    console.warn("Using default icon");
                    icon.src = "./icons/day/113.png";
                    icon.onerror = null; // Prevent infinite loop
                };
            };
        } else {
            // Fallback to default icon
            icon.src = `./icons/${timeOfDay}/113.png`;
        }
        
        // Enhanced weather details with better formatting
        cloudOutput.innerHTML = Math.round(data.current.cloud) + "%";
        humidityOutput.innerHTML = Math.round(data.current.humidity) + "%";
        windOutput.innerHTML = Math.round(data.current.wind_kph) + "km/h";
        
        const code = data.current.condition.code; 
        updateAppTheme(code, timeOfDay);
        
        // Display enhanced analysis if available
        if (data.analysis) {
            displayWeatherInsights(data.analysis);
        }
        
        app.style.opacity = "1";
        console.log("✅ Weather data updated successfully");
        
    } catch (error) {
        console.error('❌ Error fetching weather data:', error);
        handleWeatherError(error);
    }
}

// New function to handle errors more gracefully
function handleWeatherError(error) {
    temp.innerHTML = "N/A";
    conditionOutput.innerHTML = "Unable to load weather data";
    nameOutput.innerHTML = cityInput;
    
    // Better error date/time handling
    const now = new Date();
    dateOutput.innerHTML = now.toLocaleDateString();
    timeOutput.innerHTML = now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    
    // Enhanced error message logic
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
    
    alert(errorMsg);
    app.style.opacity = "1";
}

// Keep your existing updateAppTheme function exactly as is
function updateAppTheme(code, timeOfDay) {
    if(code == 1000) { 
        // Clear weather
        app.style.backgroundImage = `url(./images/${timeOfDay}/clear.jpg)`;
        btn.style.background = "#e5ba92";
        if(timeOfDay == "night") {
            btn.style.background = "#181e27";
        }
    }
    // Cloudy weather
    else if (
        code == 1003 ||
        code == 1006 ||
        code == 1009 ||
        code == 1030 ||
        code == 1069 ||
        code == 1087 ||
        code == 1135 ||
        code == 1273 ||
        code == 1276 ||
        code == 1279 ||
        code == 1282
    ) {
        app.style.backgroundImage = `url(./images/${timeOfDay}/cloudy.jpg)`;
        btn.style.background = "#fa6d1b";
        if(timeOfDay == "night") {
            btn.style.background = "#181e27";
        }
    }
    // Rainy weather
    else if (
        code == 1063 ||
        code == 1069 ||
        code == 1072 ||
        code == 1150 ||
        code == 1153 ||
        code == 1180 ||
        code == 1183 ||
        code == 1186 ||
        code == 1189 ||
        code == 1192 ||
        code == 1195 ||
        code == 1204 ||
        code == 1207 ||
        code == 1240 ||
        code == 1243 ||
        code == 1246 ||
        code == 1249 ||
        code == 1252 
    ) {
        app.style.backgroundImage = `url(./images/${timeOfDay}/rainy.jpg)`;
        btn.style.background = "#647d75";
        if(timeOfDay == "night") {
            btn.style.background = "#325c80";
        }
    }
    // Snow and other conditions
    else {
        app.style.backgroundImage = `url(./images/${timeOfDay}/snowy.jpg)`;
        btn.style.background = "#4d72aa";
        if(timeOfDay == "night") {
            btn.style.background = "#1b1b1b";
        }
    }
}

// New function to display weather insights (logs only, no UI changes)
function displayWeatherInsights(analysis) {
    console.log('🎯 Weather Analysis Received:');
    console.log(`   Comfort Level: ${analysis.comfort_level}`);
    
    if (analysis.recommendations && analysis.recommendations.length > 0) {
        console.log('💡 Recommendations:');
        analysis.recommendations.forEach((rec, index) => {
            console.log(`   ${index + 1}. ${rec}`);
        });
    }
    
    if (analysis.activities && analysis.activities.length > 0) {
        console.log('🎯 Suggested Activities:');
        analysis.activities.forEach((activity, index) => {
            console.log(`   ${index + 1}. ${activity}`);
        });
    }
    
    if (analysis.alerts && analysis.alerts.length > 0) {
        console.warn('⚠️ Weather Alerts:');
        analysis.alerts.forEach((alert, index) => {
            console.warn(`   ${index + 1}. ${alert}`);
        });
    }
    
    if (analysis.air_quality && analysis.air_quality.level) {
        console.log(`🌬️ Air Quality: ${analysis.air_quality.level} - ${analysis.air_quality.advice}`);
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
        
        // Show if AI-powered or fallback
        if (data.ai_powered) {
            console.log('🧠 Response powered by: Full AI');
        } else {
            console.log('⚡ Response powered by: Enhanced analysis');
        }
        
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
        // Enhanced health check with timeout
        const healthResponse = await Promise.race([
            fetch(`${API_BASE_URL}/health`),
            new Promise((_, reject) => 
                setTimeout(() => reject(new Error('Health check timeout')), 5000)
            )
        ]);
        
        const healthData = await healthResponse.json();
        console.log("✅ API Health Check:", healthData);
        
        // Display enhanced app info
        if (healthData.app_name) {
            console.log(`📱 ${healthData.app_name} v${healthData.version || '3.0'}`);
            console.log(`🤖 AI Mode: ${healthData.ai_mode}`);
            
            if (healthData.ai_available) {
                console.log("🧠 Full AI capabilities active!");
                console.log("💬 Try typing 'A' to test AI chat");
            } else if (healthData.enhanced_analysis) {
                console.log("⚡ Enhanced analysis available");
            }
            
            console.log(`🛠️ Capabilities:`, healthData.capabilities);
        }
        
        // Check AI status specifically
        try {
            const aiResponse = await fetch(`${API_BASE_URL}/ai-status`);
            const aiData = await aiResponse.json();
            console.log("🤖 AI Status:", aiData);
        } catch (e) {
            console.log("⚠️ AI status check failed");
        }
        
    } catch (error) {
        console.warn("⚠️ API health check failed:", error.message);
        console.log("📡 Proceeding with weather data fetch...");
    }
    
    // Load initial weather data
    fetchWeatherData();
    
    // Set up periodic refresh (every 10 minutes) with user-friendly logging
    setInterval(() => {
        console.log("🔄 Auto-refreshing weather data...");
        fetchWeatherData();
    }, 600000); // 10 minutes
    
    console.log("⏰ Auto-refresh enabled (every 10 minutes)");
}

// Enhanced keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Press 'R' to refresh weather
    if ((e.key === 'r' || e.key === 'R') && !e.ctrlKey && !e.altKey && !e.metaKey) {
        console.log("🔄 Manual refresh triggered via keyboard");
        fetchWeatherData();
    }
    
    // Press 'C' to show current weather data in console
    if ((e.key === 'c' || e.key === 'C') && !e.ctrlKey && !e.altKey && !e.metaKey) {
        if (currentWeatherData) {
            console.log("📊 Current Weather Data:", currentWeatherData);
            console.log(`🕐 Last Updated: ${lastUpdateTime.toLocaleString()}`);
        } else {
            console.log("❌ No weather data available");
        }
    }
    
    // Press 'A' to test chat with Addy
    if ((e.key === 'a' || e.key === 'A') && !e.ctrlKey && !e.altKey && !e.metaKey) {
        chatWithAddy(`What's the weather like in ${cityInput}?`, cityInput)
            .then(response => {
                console.log("🤖 Addy says:", response.response || response.error_message);
            });
    }
});

// Enhanced utility functions for debugging
window.addyWeather = {
    // Existing functions
    fetchWeatherData,
    chatWithAddy,
    updateAppTheme,
    currentCity: () => cityInput,
    
    // New debugging functions
    getCurrentData: () => currentWeatherData,
    getLastUpdate: () => lastUpdateTime,
    setCity: (city) => {
        cityInput = city;
        fetchWeatherData();
    },
    testChat: (message) => chatWithAddy(message, cityInput),
    refreshNow: () => fetchWeatherData(),
    
    // AI-specific functions
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
    
    // Health check function
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
console.log("   addyWeather.getCurrentData() - Current weather data");
console.log("🎹 Keyboard Shortcuts:");
console.log("   R - Refresh weather");
console.log("   C - Show current data");
console.log("   A - Test AI chat");