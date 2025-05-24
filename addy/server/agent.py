import datetime
import json
import os
from typing import Dict, List, Optional
from google.adk.agents import Agent
from google.genai import types
from .config import Config
from .weather_tool import fetch_weather_data, get_weather_forecast

# Create the Addy Weather Assistant Agent
addy_agent = Agent(
    name="addy_weather_assistant",
    model="gemini-2.0-flash-exp",
    description=(
        "Weather monitoring assistant that provides real-time weather data and analysis "
        "for any location worldwide. Specializes in comprehensive weather information."
    ),
    instruction="""
    You are Addy, a friendly and helpful weather assistant.
    
    You can:
    1. Fetch current weather data for any location worldwide
    2. Provide detailed weather forecasts
    3. Analyze weather conditions for various activities
    4. Give recommendations based on current weather
    5. Explain weather patterns and conditions
    
    Always provide helpful, accurate weather information in a conversational tone.
    Include relevant details like temperature, humidity, wind, and any notable conditions.
    When appropriate, suggest activities or precautions based on the weather.
    Keep responses friendly and informative.
    """,
    tools=[
        fetch_weather_data,
        get_weather_forecast
    ],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.4,
        max_output_tokens=600
    )
)

def chat_with_addy(message: str, location: Optional[str] = None) -> Dict:
    """
    Chat interface for the Addy weather agent
    
    Args:
        message (str): User's message/question
        location (Optional[str]): Location for weather data if needed
        
    Returns:
        Dict: Agent response with weather data and analysis
    """
    try:
        # Prepare the conversation context
        if location:
            context = f"User is asking about weather for {location}. {message}"
        else:
            context = message
        
        # Get response from agent
        response = addy_agent.send_message(context)
        
        return {
            "status": "success",
            "response": response.text,
            "location": location
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Agent error: {str(e)}"
        }