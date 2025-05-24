from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from pathlib import Path
from .agent import addy_agent, chat_with_addy
from .weather_tool import fetch_weather_data, get_weather_forecast
from .config import Config

# Create FastAPI app
app = FastAPI(
    title="Addy Weather Monitor",
    description="Weather monitoring API with AI assistant",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files from client directory
client_dir = Path(__file__).parent.parent / "client"
app.mount("/static", StaticFiles(directory=client_dir), name="static")

# Pydantic models for request bodies
class ChatRequest(BaseModel):
    message: str
    location: Optional[str] = None

class WeatherRequest(BaseModel):
    location: str

# Serve the main HTML file
@app.get("/")
async def read_root():
    """Serve the main HTML file"""
    html_file = client_dir / "index.html"
    if html_file.exists():
        return FileResponse(html_file)
    raise HTTPException(status_code=404, detail="HTML file not found")

# Serve static files (CSS, JS, images)
@app.get("/{file_path:path}")
async def serve_static_files(file_path: str):
    """Serve static files"""
    file_location = client_dir / file_path
    if file_location.exists() and file_location.is_file():
        return FileResponse(file_location)
    raise HTTPException(status_code=404, detail="File not found")

# Weather API endpoints
@app.get("/api/weather/{location}")
async def get_weather(location: str):
    """Get current weather data for a location"""
    try:
        weather_data = fetch_weather_data(location)
        if weather_data["status"] == "error":
            raise HTTPException(status_code=400, detail=weather_data["error_message"])
        return weather_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/forecast/{location}")
async def get_forecast(location: str, days: int = 3):
    """Get weather forecast for a location"""
    try:
        forecast_data = get_weather_forecast(location, days)
        if forecast_data["status"] == "error":
            raise HTTPException(status_code=400, detail=forecast_data["error_message"])
        return forecast_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """Chat with Addy agent"""
    try:
        if not request.message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        response = chat_with_addy(request.message, request.location)
        if response["status"] == "error":
            raise HTTPException(status_code=500, detail=response["error_message"])
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Simple weather endpoint that matches your frontend format
@app.get("/api/weather/simple/{location}")
async def get_simple_weather(location: str):
    """Get weather data in format compatible with existing frontend"""
    try:
        weather_data = fetch_weather_data(location)
        if weather_data["status"] == "error":
            raise HTTPException(status_code=400, detail=weather_data["error_message"])
        
        # Format data to match your existing frontend expectations
        simplified = {
            "location": {
                "name": weather_data["location"]["name"],
                "localtime": weather_data["location"]["local_time"]
            },
            "current": {
                "temp_c": weather_data["current_conditions"]["temperature_celsius"],
                "condition": {
                    "text": weather_data["weather_condition"]["description"],
                    "code": weather_data["weather_condition"]["code"],
                    "icon": weather_data["weather_condition"]["icon_url"]
                },
                "humidity": weather_data["current_conditions"]["humidity_percent"],
                "cloud": weather_data["current_conditions"]["cloud_coverage_percent"],
                "wind_kph": weather_data["current_conditions"]["wind"]["speed_kph"],
                "is_day": weather_data["environmental_indicators"]["is_daytime"]
            }
        }
        return simplified
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    config_info = Config.get_config_info()
    return {
        "status": "healthy",
        "app_name": config_info["app_name"],
        "version": config_info["app_version"],
        "weather_api_configured": config_info["weather_api_configured"]
    }

# Run the app
if __name__ == "__main__":
    import uvicorn
    
    print("Starting Addy Weather Monitor with FastAPI...")
    if Config.validate_config():
        print("Configuration validated successfully")
        uvicorn.run(
            "main:app", 
            host="0.0.0.0", 
            port=8000, 
            reload=Config.DEBUG_MODE
        )
    else:
        print("Configuration validation failed. Please check your .env file.")