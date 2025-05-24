import requests
from typing import Dict, Optional
import os
from datetime import datetime
from .config import Config

def fetch_weather_data(location: str) -> Dict:
    """
    Fetches current weather data for a specified location to inform environmental monitoring decisions.
    
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
            "aqi": "yes"  # Include air quality data for environmental monitoring
        }
        
        # Make API request
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
        
        # Add environmental analysis for mangrove monitoring
        weather_info["mangrove_environmental_assessment"] = analyze_mangrove_conditions(weather_info)
        
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

def analyze_mangrove_conditions(weather_data: Dict) -> Dict:
    """
    Analyzes weather conditions specifically for mangrove ecosystem monitoring.
    
    Args:
        weather_data (Dict): Current weather data
        
    Returns:
        Dict: Environmental assessment for mangrove health
    """
    try:
        temp = weather_data["current_conditions"]["temperature_celsius"]
        humidity = weather_data["current_conditions"]["humidity_percent"]
        precipitation = weather_data["environmental_indicators"]["precipitation_mm"]
        wind_speed = weather_data["current_conditions"]["wind"]["speed_kph"]
        
        assessment = {
            "temperature_suitability": "optimal" if 20 <= temp <= 35 else "suboptimal" if temp < 20 or temp > 35 else "stress_conditions",
            "humidity_status": "ideal" if humidity >= 60 else "low" if humidity >= 40 else "very_low",
            "precipitation_level": "high" if precipitation > 5 else "moderate" if precipitation > 1 else "low",
            "wind_conditions": "calm" if wind_speed < 10 else "moderate" if wind_speed < 25 else "strong",
            "overall_conditions": "favorable",
            "recommendations": []
        }
        
        # Generate recommendations based on conditions
        if temp > 35:
            assessment["recommendations"].append("Monitor for heat stress in mangrove vegetation")
        if temp < 20:
            assessment["recommendations"].append("Cold conditions may affect mangrove growth")
        if humidity < 40:
            assessment["recommendations"].append("Low humidity may stress mangrove ecosystems")
        if wind_speed > 25:
            assessment["recommendations"].append("Strong winds may cause physical damage to mangrove structures")
        if precipitation > 10:
            assessment["recommendations"].append("Heavy rainfall may cause flooding and sedimentation")
        
        # Determine overall conditions
        stress_factors = sum([
            temp > 35 or temp < 20,
            humidity < 40,
            wind_speed > 25,
            precipitation > 15
        ])
        
        if stress_factors == 0:
            assessment["overall_conditions"] = "excellent"
        elif stress_factors <= 1:
            assessment["overall_conditions"] = "good"
        elif stress_factors <= 2:
            assessment["overall_conditions"] = "fair"
        else:
            assessment["overall_conditions"] = "challenging"
            
        return assessment
        
    except Exception as e:
        return {
            "error": f"Could not analyze mangrove conditions: {str(e)}"
        }

def get_weather_forecast(location: str, days: int = 3) -> Dict:
    """
    Fetches weather forecast data for environmental planning.
    
    Args:
        location (str): Location for forecast
        days (int): Number of days for forecast (1-10)
        
    Returns:
        Dict: Forecast data for environmental monitoring
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
                "uv_index": day["day"]["uv"],
                "mangrove_suitability": "good" if 20 <= day["day"]["avgtemp_c"] <= 35 and day["day"]["avghumidity"] >= 60 else "moderate"
            }
            forecast_info["daily_forecasts"].append(day_info)
            
        return forecast_info
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Could not fetch forecast for '{location}': {str(e)}"
        }