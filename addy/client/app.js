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

// Add click event to each city in the panel
cities.forEach((city) => {
    city.addEventListener('click', (e) => {
        // Change from default city to the clicked one
        cityInput = e.target.innerHTML;
        fetchWeatherData();
        // Fade out the app (simple animation)
        app.style.opacity = "0";
    });
});

// Add submit event to the form
form.addEventListener('submit', (e) => {
    // If the input field (search bar) is empty, throw an alert
    if(search.value.length == 0) {
        alert('Please type in a city name');
    } else {
        // Change from default city to the one written in the input field
        cityInput = search.value;
        fetchWeatherData();
        // Remove all text from the input field
        search.value = "";
        // Fade out the app (simple animation)
        app.style.opacity = "0";
    }
    
    // Prevents the default behaviour of the form
    e.preventDefault();
});

// Function that returns a day of the week from a date
function dayOfTheWeek(day, month, year) {
    const weekday = [
        "Sunday", 
        "Monday", 
        "Tuesday", 
        "Wednesday", 
        "Thursday", 
        "Friday", 
        "Saturday"
    ];
    return weekday[new Date(`${day}/${month}/${year}`).getDay()];
}

// Function that fetches and displays the data from our FastAPI backend
async function fetchWeatherData() {
    try {
        console.log(`Fetching weather data for: ${cityInput}`);
        
        // Show loading state
        temp.innerHTML = "Loading...";
        conditionOutput.innerHTML = "Fetching weather data...";
        nameOutput.innerHTML = "Loading...";
        
        // Fetch data from our FastAPI backend
        const response = await fetch(`${API_BASE_URL}/weather/simple/${encodeURIComponent(cityInput)}`);
        
        console.log(`Response status: ${response.status}`);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: "Unknown error" }));
            throw new Error(`HTTP ${response.status}: ${errorData.detail || response.statusText}`);
        }
        
        const data = await response.json();
        console.log('Weather data received:', data);
        
        // Validate data structure
        if (!data.current || !data.location) {
            throw new Error("Invalid weather data format received");
        }
        
        // Update temperature and condition
        temp.innerHTML = data.current.temp_c + "&#176;";
        conditionOutput.innerHTML = data.current.condition.text;
        
        // Get the date and time from the city
        const date = data.location.localtime;
        const y = parseInt(date.substr(0, 4));
        const m = parseInt(date.substr(5, 2));
        const d = parseInt(date.substr(8, 2));
        const time = date.substr(11); 
        
        // Reformat the date and add it to the page
        dateOutput.innerHTML = `${dayOfTheWeek(d, m, y)} ${d}/${m}/${y}`;
        timeOutput.innerHTML = time;
        
        // Add the name of the city
        nameOutput.innerHTML = data.location.name;
        
        // Set weather icon
        const iconUrl = data.current.condition.icon;
        if (iconUrl.includes("cdn.weatherapi.com")) {
            const iconId = iconUrl.split("/").pop();
            icon.src = "./icons/" + iconId;
        } else {
            icon.src = "./icons/day/113.png"; // Default icon
        }
        
        // Add the weather details
        cloudOutput.innerHTML = data.current.cloud + "%";
        humidityOutput.innerHTML = data.current.humidity + "%";
        windOutput.innerHTML = data.current.wind_kph + "km/h";
        
        // Set default time of day
        let timeOfDay = "day";
        // Get the unique id for each weather condition
        const code = data.current.condition.code; 
        
        // Change to night if its night time in the city
        if(!data.current.is_day) {
            timeOfDay = "night";
        } 
        
        // Set background based on weather conditions
        updateAppTheme(code, timeOfDay);
        
        // Fade in the page once all is done
        app.style.opacity = "1";
        
        console.log("Weather data updated successfully");
        
    } catch (error) {
        console.error('Error fetching weather data:', error);
        
        // Show error in UI
        temp.innerHTML = "Error";
        conditionOutput.innerHTML = "Unable to load weather data";
        nameOutput.innerHTML = cityInput;
        
        // Show user-friendly message
        alert(`Unable to fetch weather data for "${cityInput}". Please check the city name and try again.`);
        
        app.style.opacity = "1";
    }
}

// Function to update app theme based on weather
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

// Chat with Addy agent function
async function chatWithAddy(message, location = null) {
    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                location: location
            })
        });
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error chatting with Addy:', error);
        return {
            status: "error",
            error_message: "Failed to communicate with Addy agent"
        };
    }
}

// Initialize the app
async function initializeApp() {
    console.log("Initializing Addy Weather Monitor...");
    
    // Check if API is available
    try {
        const healthResponse = await fetch(`${API_BASE_URL}/health`);
        const healthData = await healthResponse.json();
        console.log("API Health:", healthData);
    } catch (error) {
        console.warn("API health check failed:", error);
    }
    
    // Load initial weather data
    fetchWeatherData();
}

// Call the initialization function on page load
document.addEventListener('DOMContentLoaded', initializeApp);