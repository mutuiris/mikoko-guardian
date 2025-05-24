import datetime
import json
import os
from typing import Dict, List, Optional
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
from google.generativeai import GenerativeModel
from google.genai import types
import vertexai
from vertexai.preview import reasoning_engines

# Import the weather tool
from .weather_tool import fetch_weather_data, get_weather_forecast, analyze_mangrove_conditions

# Create the Addy Weather and Environmental Monitoring Agent
addy_agent = Agent(
    name="addy_weather_monitor",
    model="gemini-2.0-flash-exp",
    description=(
        "Environmental monitoring agent that provides real-time weather data and analysis "
        "for coastal Kenya. Specializes in weather conditions affecting mangrove ecosystems, "
        "carbon sequestration environments, and coastal conservation planning."
    ),
    instruction="""
    You are Addy, an environmental monitoring assistant focused on weather data analysis for coastal Kenya.
    
    You can:
    1. Fetch current weather data for any location in Kenya (especially coastal areas)
    2. Analyze weather conditions for mangrove ecosystem health
    3. Provide weather forecasts for environmental planning
    4. Assess environmental indicators affecting conservation efforts
    5. Recommend actions based on weather conditions for field work and monitoring
    
    Focus on:
    - Temperature, humidity, and precipitation impacts on mangrove health
    - Air quality monitoring for environmental assessment
    - Wind patterns affecting coastal ecosystems
    - Weather suitability for conservation activities
    - Climate conditions supporting carbon sequestration
    
    Always provide practical recommendations based on current weather conditions.
    """,
    tools=[
        fetch_weather_data,
        get_weather_forecast
    ],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.3,
        max_output_tokens=400
    )
)

