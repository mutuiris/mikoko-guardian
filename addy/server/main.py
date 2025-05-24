from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import sys
from pathlib import Path

# Add the current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import configuration
try:
    from config import Config
except ImportError as e:
    print(f"Config import error: {e}")
    sys.exit(1)

# Import weather tool
try:
    from weather_tool import fetch_weather_data, get_weather_forecast
except ImportError as e:
    print(f"Weather tool import error: {e}")
    sys.exit(1)

# Create FastAPI app
app = FastAPI(
    title="Addy Weather Monitor",
    description="Weather monitoring API with AI assistant",
    version="1.0.0"
)

# Add CORS middleware - Allow frontend on port 3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Get the client directory path
client_dir = current_dir.parent / "client"

# Pydantic models for request bodies
class ChatRequest(BaseModel):
    message: str
    location: Optional[str] = None

class WeatherRequest(BaseModel):
    location: str

# API ROUTES FIRST (more specific routes come first)
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

# Simple weather endpoint that matches your frontend format
@app.get("/api/weather/simple/{location}")
async def get_simple_weather(location: str):
    """Get weather data in format compatible with existing frontend"""
    try:
        print(f"API: Fetching simple weather for: {location}")  # Debug log
        weather_data = fetch_weather_data(location)
        
        if weather_data["status"] == "error":
            print(f"Weather error: {weather_data['error_message']}")
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
        
        print(f"Returning simplified data for {location}")  # Debug log
        return simplified
        
    except Exception as e:
        print(f"Exception in get_simple_weather: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/weather/{location}")
async def get_weather(location: str):
    """Get current weather data for a location"""
    try:
        print(f"API: Fetching weather for: {location}")  # Debug log
        weather_data = fetch_weather_data(location)
        
        if weather_data["status"] == "error":
            print(f"Weather API error: {weather_data['error_message']}")
            raise HTTPException(status_code=400, detail=weather_data["error_message"])
        
        return weather_data
    except Exception as e:
        print(f"Exception in get_weather: {str(e)}")
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
        
        # For now, return a simple response since Google AI might not be available
        return {
            "status": "success",
            "response": f"Weather assistant here! You asked: '{request.message}'. I'm currently focusing on weather data for {request.location if request.location else 'your location'}.",
            "location": request.location
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# STATIC FILE ROUTES (these come after API routes)
# Mount static files from client directory
if client_dir.exists():
    app.mount("/static", StaticFiles(directory=client_dir), name="static")

# Serve the main HTML file
@app.get("/")
async def read_root():
    """Serve the main HTML file"""
    html_file = client_dir / "index.html"
    if html_file.exists():
        return FileResponse(html_file)
    raise HTTPException(status_code=404, detail="HTML file not found")

# Serve specific static files
@app.get("/style.css")
async def serve_css():
    css_file = client_dir / "style.css"
    if css_file.exists():
        return FileResponse(css_file)
    raise HTTPException(status_code=404, detail="CSS file not found")

@app.get("/app.js")
async def serve_js():
    js_file = client_dir / "app.js"
    if js_file.exists():
        return FileResponse(js_file)
    raise HTTPException(status_code=404, detail="JS file not found")

# Serve icons directory
@app.get("/icons/{file_path:path}")
async def serve_icons(file_path: str):
    icon_file = client_dir / "icons" / file_path
    if icon_file.exists() and icon_file.is_file():
        return FileResponse(icon_file)
    raise HTTPException(status_code=404, detail="Icon not found")

# Serve images directory
@app.get("/images/{file_path:path}")
async def serve_images(file_path: str):
    image_file = client_dir / "images" / file_path
    if image_file.exists() and image_file.is_file():
        return FileResponse(image_file)
    raise HTTPException(status_code=404, detail="Image not found")

# Catch-all for other static files (this should be last)
@app.get("/{file_path:path}")
async def serve_static_files(file_path: str):
    """Serve other static files"""
    # Prevent serving files outside client directory
    if ".." in file_path or file_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="File not found")
    
    file_location = client_dir / file_path
    if file_location.exists() and file_location.is_file():
        return FileResponse(file_location)
    
    raise HTTPException(status_code=404, detail="File not found")

# Run the app
if __name__ == "__main__":
    import uvicorn
    
    print("=" * 50)
    print("🌤️  ADDY WEATHER MONITOR")
    print("=" * 50)
    print(f"Client directory: {client_dir}")
    
    if Config.validate_config():
        print("✅ Configuration validated successfully")
        print("🚀 Starting FastAPI server...")
        print("📍 Server: http://localhost:8000")
        print("🌐 API docs: http://localhost:8000/docs")
        print("-" * 50)
        
        uvicorn.run(
            "main:app", 
            host="0.0.0.0", 
            port=8000, 
            reload=Config.DEBUG_MODE
        )
    else:
        print("❌ Configuration validation failed. Please check your .env file.")