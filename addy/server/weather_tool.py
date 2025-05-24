import requests
from typing import Dict, Optional
import os
from datetime import datetime
from .config import Config

def fetch_weather_data(location: str) -> Dict:
    """
    Fetches current weather data for a specified location.
    
    Args:
        location (str): City name or coordinates for weather data retrieval.
        
    Returns:
        Dict: Structured weather information including temperature, humidity, rainfall, and environmental indicators.
    """
    try:
        # Validate configuration
        if not Config.WEATHER_API_KEY:
            return {
                "status": "error",
                "error_message": "Weather API key not configured. Please check your .env file."
            }
        
        # Validate input
        if not location or not isinstance(location, str):
            return {
                "status": "error",
                "error_message": "Please provide a valid location name."
            }
        
        # Prepare API request
        params = {
            "key": Config.WEATHER_API_KEY,
            "q": location.strip(),
            "aqi": "yes"
        }
        
        response = requests.get(Config.WEATHER_API_BASE_URL, params=params, timeout=Config.API_TIMEOUT_SECONDS)
        response.raise_for_status()
        
        data = response.json()
        
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
        
        return weather_info
        
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error_message": f"Failed to fetch weather data: Network error - {str(e)}"
        }
    except requests.exceptions.HTTPError as e:
        return {
            "status": "error", 
            "error_message": f"Weather API error: {str(e)}"
        }
    except KeyError as e:
        return {
            "status": "error",
            "error_message": f"Unexpected weather data format: Missing field {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Location '{location}' not found or weather data unavailable."
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
            day_info = {
                "date": day["date"],
                "max_temp_c": day["day"]["maxtemp_c"],
                "min_temp_c": day["day"]["mintemp_c"],
                "avg_humidity": day["day"]["avghumidity"],
                "total_precipitation_mm": day["day"]["totalprecip_mm"],
                "max_wind_kph": day["day"]["maxwind_kph"],
                "condition": day["day"]["condition"]["text"],
                "uv_index": day["day"]["uv"]
            }
            forecast_info["daily_forecasts"].append(day_info)
            
        return forecast_info
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Could not fetch forecast for '{location}': {str(e)}"
        }