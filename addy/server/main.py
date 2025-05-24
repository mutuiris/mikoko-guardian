from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import sys
from pathlib import Path
import asyncio

# Add the current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import configuration
try:
    from config import Config
except ImportError as e:
    print(f"Config import error: {e}")
    sys.exit(1)

# Import weather tools and agents
try:
    from weather_tool import fetch_weather_data, get_weather_forecast
    from enhanced_weather_agent import enhanced_addy, chat_with_enhanced_addy, get_enhanced_weather_analysis
except ImportError as e:
    print(f"Enhanced agent import error: {e}")
    enhanced_addy = None
    chat_with_enhanced_addy = None
    get_enhanced_weather_analysis = None

# Import AI agent
try:
    from ai_agent import chat_with_ai_addy, get_ai_capabilities, ai_addy
    AI_AGENT_AVAILABLE = True
    print("✅ Full AI agent imported successfully")
except ImportError as e:
    print(f"⚠️ Full AI agent not available: {e}")
    AI_AGENT_AVAILABLE = False

# Create FastAPI app
app = FastAPI(
    title="Addy Weather Monitor v3.0",
    description="Full AI-powered weather monitoring with intelligent assistant",
    version="3.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Get the client directory path
client_dir = current_dir.parent / "client"

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    location: Optional[str] = None

class WeatherRequest(BaseModel):
    location: str

# API ROUTES
@app.get("/api/health")
async def health_check():
    """Enhanced health check endpoint"""
    config_info = Config.get_config_info()
    
    ai_status = "Full AI" if AI_AGENT_AVAILABLE else "Enhanced Analysis" if enhanced_addy else "Basic"
    
    return {
        "status": "healthy",
        "app_name": config_info["app_name"],
        "version": "3.0.0",
        "ai_mode": ai_status,
        "ai_available": AI_AGENT_AVAILABLE,
        "enhanced_analysis": enhanced_addy is not None,
        "weather_api_configured": config_info["weather_api_configured"],
        "google_api_configured": config_info["google_api_configured"],
        "capabilities": get_ai_capabilities()["features"] if AI_AGENT_AVAILABLE else (enhanced_addy.capabilities if enhanced_addy else ["Basic weather data"])
    }

@app.get("/api/ai-status")
async def ai_status():
    """Get AI capabilities status"""
    if AI_AGENT_AVAILABLE:
        return get_ai_capabilities()
    else:
        return {
            "ai_available": False,
            "message": "Full AI capabilities not available",
            "fallback_mode": "Enhanced weather analysis" if enhanced_addy else "Basic mode"
        }

@app.get("/api/weather/simple/{location}")
async def get_simple_weather(location: str):
    """Get weather data with enhanced analysis"""
    try:
        print(f"🌤️ API: Fetching enhanced weather for: {location}")
        weather_data = fetch_weather_data(location)
        
        if weather_data["status"] == "error":
            print(f"❌ Weather error: {weather_data['error_message']}")
            raise HTTPException(status_code=400, detail=weather_data["error_message"])
        
        # Get enhanced analysis if available
        analysis = None
        if enhanced_addy:
            try:
                analysis_result = enhanced_addy.analyze_weather_comprehensive(weather_data)
                analysis = {
                    "comfort_level": analysis_result.comfort_level,
                    "recommendations": analysis_result.recommendations[:3],
                    "activities": analysis_result.activities[:3],
                    "alerts": analysis_result.alerts,
                    "summary": analysis_result.summary,
                    "air_quality": analysis_result.air_quality_info
                }
            except Exception as e:
                print(f"⚠️ Analysis error: {e}")
        
        # Format data for frontend
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
        
        # Add analysis if available
        if analysis:
            simplified["analysis"] = analysis
        
        print(f"✅ Returning enhanced data for {location}")
        return simplified
        
    except Exception as e:
        print(f"💥 Exception in get_simple_weather: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """Full AI-powered chat with Addy agent"""
    try:
        if not request.message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        print(f"💬 AI Chat request: '{request.message}' for {request.location}")
        
        if AI_AGENT_AVAILABLE:
            # Use full AI capabilities
            response = await chat_with_ai_addy(request.message, request.location)
            print(f"🤖 AI-powered response generated")
        elif chat_with_enhanced_addy:
            # Use enhanced analysis
            response = chat_with_enhanced_addy(request.message, request.location)
            response["ai_powered"] = False
            print(f"🧠 Enhanced analysis response generated")
        else:
            # Basic fallback
            response = {
                "status": "success",
                "response": f"Hello! I'm Addy. You asked: '{request.message}'. I'm currently in basic mode.",
                "ai_powered": False,
                "location": request.location
            }
        
        return response
        
    except Exception as e:
        print(f"💥 Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/weather/analysis/{location}")
async def get_weather_analysis(location: str):
    """Get comprehensive weather analysis"""
    try:
        if not enhanced_addy:
            raise HTTPException(status_code=503, detail="Enhanced analysis not available")
        
        result = get_enhanced_weather_analysis(location)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["error_message"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/weather/{location}")
async def get_weather(location: str):
    """Get complete weather data"""
    try:
        weather_data = fetch_weather_data(location)
        if weather_data["status"] == "error":
            raise HTTPException(status_code=400, detail=weather_data["error_message"])
        return weather_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/forecast/{location}")
async def get_forecast(location: str, days: int = 3):
    """Get weather forecast"""
    try:
        forecast_data = get_weather_forecast(location, days)
        if forecast_data["status"] == "error":
            raise HTTPException(status_code=400, detail=forecast_data["error_message"])
        return forecast_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# STATIC FILE ROUTES
if client_dir.exists():
    app.mount("/static", StaticFiles(directory=client_dir), name="static")

@app.get("/")
async def read_root():
    html_file = client_dir / "index.html"
    if html_file.exists():
        return FileResponse(html_file)
    raise HTTPException(status_code=404, detail="HTML file not found")

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

# FIXED ICON SERVING - Handle day/night subfolders
@app.get("/icons/{icon_name}")
async def serve_icon_smart(icon_name: str):
    """Smart icon serving - tries day folder first, then night folder"""
    icons_dir = client_dir / "icons"
    
    # Try day folder first
    day_icon = icons_dir / "day" / icon_name
    if day_icon.exists():
        return FileResponse(day_icon)
    
    # Try night folder
    night_icon = icons_dir / "night" / icon_name
    if night_icon.exists():
        return FileResponse(night_icon)
    
    # Fallback to default icon
    default_icon = icons_dir / "day" / "113.png"
    if default_icon.exists():
        return FileResponse(default_icon)
    
    raise HTTPException(status_code=404, detail="Icon not found")

@app.get("/icons/{time_of_day}/{icon_name}")
async def serve_icon_specific(time_of_day: str, icon_name: str):
    """Serve specific day/night icons"""
    if time_of_day not in ["day", "night"]:
        raise HTTPException(status_code=400, detail="Invalid time of day")
    
    icon_file = client_dir / "icons" / time_of_day / icon_name
    if icon_file.exists():
        return FileResponse(icon_file)
    
    # Fallback to day version
    fallback_icon = client_dir / "icons" / "day" / icon_name
    if fallback_icon.exists():
        return FileResponse(fallback_icon)
    
    raise HTTPException(status_code=404, detail="Icon not found")

@app.get("/images/{file_path:path}")
async def serve_images(file_path: str):
    image_file = client_dir / "images" / file_path
    if image_file.exists() and image_file.is_file():
        return FileResponse(image_file)
    raise HTTPException(status_code=404, detail="Image not found")

@app.get("/{file_path:path}")
async def serve_static_files(file_path: str):
    if ".." in file_path or file_path.startswith("api/"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    file_location = client_dir / file_path
    if file_location.exists() and file_location.is_file():
        return FileResponse(file_location)
    
    raise HTTPException(status_code=404, detail="File not found")

# Run the app
if __name__ == "__main__":
    import uvicorn
        
    print("=" * 60)
    print("🌤️  ADDY WEATHER MONITOR v3.0 - FULL AI")
    print("=" * 60)
    
    if AI_AGENT_AVAILABLE:
        print(f"🤖 Full AI Agent: {ai_addy.name} v{ai_addy.version}")
        print("🧠 Capabilities: Natural language conversations, context memory, adaptive responses")
    elif enhanced_addy:
        print(f"🧠 Enhanced Agent: {enhanced_addy.name} v{enhanced_addy.version}")
        print("⚡ Capabilities: Advanced weather analysis, recommendations, alerts")
    else:
        print("📊 Basic Mode: Weather data only")
    
    print(f"📁 Client: {client_dir}")
    print(f"🌐 Icons: Fixed day/night folder handling")
    
    if Config.validate_config():
        print("✅ Configuration validated successfully")
        print("🚀 Starting full AI FastAPI server...")
        print("📍 Server: http://localhost:8000")
        print("🌐 API docs: http://localhost:8000/docs")
        print("🔧 Health: http://localhost:8000/api/health")
        print("💬 AI Chat: http://localhost:8000/api/chat")
        print("🤖 AI Status: http://localhost:8000/api/ai-status")
        print("-" * 60)
        
        uvicorn.run(
            "main:app", 
            host="0.0.0.0", 
            port=8000, 
            reload=Config.DEBUG_MODE
        )
    else:
        print("❌ Configuration validation failed. Please check your .env file.")