import requests
import os
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path

# Handle imports properly
try:
    from .config import Config
except ImportError:
    # If relative import fails, try absolute import
    try:
        from config import Config
    except ImportError:
        # If that fails too, create a minimal config
        print("Warning: Using fallback config")
        class Config:
            WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '')
            WEATHER_API_BASE_URL = os.getenv('WEATHER_API_BASE_URL', 'https://api.weatherapi.com/v1/current.json')
            WEATHER_FORECAST_URL = os.getenv('WEATHER_FORECAST_URL', 'https://api.weatherapi.com/v1/forecast.json')
            API_TIMEOUT_SECONDS = int(os.getenv('API_TIMEOUT_SECONDS', '10'))
            MAX_FORECAST_DAYS = int(os.getenv('MAX_FORECAST_DAYS', '10'))

def fetch_weather_data(location: str) -> Dict:
    """
    Fetches current weather data for a specified location.
    
    Args:
        location (str): City name or coordinates for weather data retrieval.
        
    Returns:
        Dict: Structured weather information including temperature, humidity, rainfall, and environmental indicators.
    """
    try:
        print(f"WEATHER_TOOL: Starting fetch for {location}")
        
        # Validate configuration
        if not Config.WEATHER_API_KEY:
            error_msg = "Weather API key not configured. Please check your .env file."
            print(f"WEATHER_TOOL ERROR: {error_msg}")
            return {
                "status": "error",
                "error_message": error_msg
            }
        
        # Validate input
        if not location or not isinstance(location, str):
            error_msg = "Please provide a valid location name."
            print(f"WEATHER_TOOL ERROR: {error_msg}")
            return {
                "status": "error",
                "error_message": error_msg
            }
        
        # Prepare API request
        params = {
            "key": Config.WEATHER_API_KEY,
            "q": location.strip(),
            "aqi": "yes"
        }
        
        print(f"WEATHER_TOOL: Making API request to: {Config.WEATHER_API_BASE_URL}")
        print(f"WEATHER_TOOL: Location: {location}")
        
        response = requests.get(Config.WEATHER_API_BASE_URL, params=params, timeout=Config.API_TIMEOUT_SECONDS)
        
        print(f"WEATHER_TOOL: Response status: {response.status_code}")
        
        response.raise_for_status()
        
        data = response.json()
        print(f"WEATHER_TOOL: Successfully fetched data for {data['location']['name']}")
        
        # Extract and structure relevant weather data
        weather_info = {
            "status": "success",
            "location": {
                "name": data["location"]["name"],
                "region": data["location"]["region"],
                "country": data["location"]["country"],
                "coordinates": {
                    "latitude": data["location"]["lat"],
                    "longitude": data["location"]["lon"]
                },
                "local_time": data["location"]["localtime"]
            },
            "current_conditions": {
                "temperature_celsius": data["current"]["temp_c"],
                "temperature_fahrenheit": data["current"]["temp_f"],
                "feels_like_celsius": data["current"]["feelslike_c"],
                "humidity_percent": data["current"]["humidity"],
                "cloud_coverage_percent": data["current"]["cloud"],
                "visibility_km": data["current"]["vis_km"],
                "uv_index": data["current"]["uv"],
                "wind": {
                    "speed_kph": data["current"]["wind_kph"],
                    "speed_mph": data["current"]["wind_mph"],
                    "direction": data["current"]["wind_dir"],
                    "degree": data["current"]["wind_degree"],
                    "gust_kph": data["current"]["gust_kph"]
                }
            },
            "weather_condition": {
                "description": data["current"]["condition"]["text"],
                "code": data["current"]["condition"]["code"],
                "icon_url": data["current"]["condition"]["icon"]
            },
            "environmental_indicators": {
                "is_daytime": bool(data["current"]["is_day"]),
                "pressure_mb": data["current"]["pressure_mb"],
                "pressure_inches": data["current"]["pressure_in"],
                "precipitation_mm": data["current"]["precip_mm"],
                "precipitation_inches": data["current"]["precip_in"]
            }
        }
        
        # Add air quality data if available
        if "air_quality" in data["current"]:
            weather_info["air_quality"] = {
                "co_μgm3": data["current"]["air_quality"].get("co", "N/A"),
                "no2_μgm3": data["current"]["air_quality"].get("no2", "N/A"),
                "o3_μgm3": data["current"]["air_quality"].get("o3", "N/A"),
                "so2_μgm3": data["current"]["air_quality"].get("so2", "N/A"),
                "pm2_5_μgm3": data["current"]["air_quality"].get("pm2_5", "N/A"),
                "pm10_μgm3": data["current"]["air_quality"].get("pm10", "N/A"),
                "us_epa_index": data["current"]["air_quality"].get("us-epa-index", "N/A"),
                "gb_defra_index": data["current"]["air_quality"].get("gb-defra-index", "N/A")
            }
        
        print(f"WEATHER_TOOL: Successfully processed data for {location}")
        return weather_info
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to fetch weather data: Network error - {str(e)}"
        print(f"WEATHER_TOOL REQUEST ERROR: {error_msg}")
        return {
            "status": "error",
            "error_message": error_msg
        }
    except requests.exceptions.HTTPError as e:
        error_msg = f"Weather API error: {str(e)}"
        print(f"WEATHER_TOOL HTTP ERROR: {error_msg}")
        return {
            "status": "error", 
            "error_message": error_msg
        }
    except KeyError as e:
        error_msg = f"Unexpected weather data format: Missing field {str(e)}"
        print(f"WEATHER_TOOL KEY ERROR: {error_msg}")
        return {
            "status": "error",
            "error_message": error_msg
        }
    except Exception as e:
        error_msg = f"Location '{location}' not found or weather data unavailable: {str(e)}"
        print(f"WEATHER_TOOL GENERAL ERROR: {error_msg}")
        return {
            "status": "error",
            "error_message": error_msg
        }

def get_weather_forecast(location: str, days: int = 3) -> Dict:
    """
    Fetches weather forecast data for planning.
    
    Args:
        location (str): Location for forecast
        days (int): Number of days for forecast (1-10)
        
    Returns:
        Dict: Forecast data
    """
    try:
        if not Config.WEATHER_API_KEY:
            return {
                "status": "error",
                "error_message": "Weather API key not configured. Please check your .env file."
            }
            
        if days < 1 or days > Config.MAX_FORECAST_DAYS:
            return {
                "status": "error",
                "error_message": f"Forecast days must be between 1 and {Config.MAX_FORECAST_DAYS}"
            }
            
        params = {
            "key": Config.WEATHER_API_KEY,
            "q": location.strip(),
            "days": days,
            "aqi": "yes"
        }
        
        response = requests.get(Config.WEATHER_FORECAST_URL, params=params, timeout=Config.API_TIMEOUT_SECONDS)
        response.raise_for_status()
        
        data = response.json()
        
        forecast_info = {
            "status": "success",
            "location": data["location"]["name"],
            "forecast_days": days,
            "daily_forecasts": []
        }
        
        for day in data["forecast"]["forecastday"]:
            daily_forecast = {
                "date": day["date"],
                "max_temp_c": day["day"]["maxtemp_c"],
                "min_temp_c": day["day"]["mintemp_c"],
                "condition": day["day"]["condition"]["text"],
                "chance_of_rain": day["day"]["daily_chance_of_rain"],
                "total_precipitation_mm": day["day"]["totalprecip_mm"]
            }
            forecast_info["daily_forecasts"].append(daily_forecast)
            
        return forecast_info
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Could not fetch forecast for '{location}': {str(e)}"
        }