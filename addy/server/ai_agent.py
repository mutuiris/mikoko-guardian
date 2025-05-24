import google.generativeai as genai
import json
from typing import Dict, List, Optional
from datetime import datetime
import asyncio

# Configure Gemini
try:
    from config import Config
    genai.configure(api_key=Config.GOOGLE_API_KEY)
    
    # Create the model
    model = genai.GenerativeModel('gemini-pro')
    GEMINI_AVAILABLE = True
    print("✅ Gemini Pro AI initialized successfully")
except Exception as e:
    print(f"❌ Gemini initialization failed: {e}")
    GEMINI_AVAILABLE = False

class FullAIAddyAgent:
    """Full AI-powered Addy Weather Agent using Gemini Pro"""
    
    def __init__(self):
        self.name = "Addy AI"
        self.version = "3.0"
        self.conversation_history = []
        self.personality = """
        You are Addy, an intelligent weather assistant with a friendly, helpful personality.
        
        Your capabilities:
        - Provide comprehensive weather analysis and forecasts
        - Give personalized recommendations based on user preferences
        - Explain weather phenomena in simple terms
        - Suggest activities based on weather conditions
        - Provide safety alerts and health advice
        - Remember conversation context for better assistance
        
        Your personality:
        - Friendly and conversational
        - Knowledgeable but not overwhelming
        - Helpful and proactive
        - Uses appropriate emojis and formatting
        - Adapts tone based on weather conditions (cheerful for good weather, caring for severe weather)
        """
    
    async def chat(self, message: str, location: Optional[str] = None, weather_data: Optional[Dict] = None) -> Dict:
        """
        Full AI-powered conversation with context awareness
        """
        try:
            if not GEMINI_AVAILABLE:
                return self._fallback_response(message, location)
            
            # Build context prompt
            context = self._build_context_prompt(message, location, weather_data)
            
            # Generate AI response
            response = model.generate_content(context)
            
            # Store conversation history
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user_message": message,
                "location": location,
                "ai_response": response.text
            })
            
            # Keep only last 10 exchanges
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return {
                "status": "success",
                "response": response.text,
                "ai_powered": True,
                "conversation_id": len(self.conversation_history),
                "location": location
            }
            
        except Exception as e:
            print(f"AI Error: {e}")
            return self._fallback_response(message, location)
    
    def _build_context_prompt(self, message: str, location: Optional[str], weather_data: Optional[Dict]) -> str:
        """Build comprehensive context prompt for AI"""
        
        prompt = f"{self.personality}\n\n"
        
        # Add weather data context if available
        if weather_data and weather_data.get("status") == "success":
            current = weather_data["current_conditions"]
            condition = weather_data["weather_condition"]
            env = weather_data["environmental_indicators"]
            
            prompt += f"""
CURRENT WEATHER DATA for {location}:
- Temperature: {current['temperature_celsius']}°C (feels like {current['feels_like_celsius']}°C)
- Condition: {condition['description']}
- Humidity: {current['humidity_percent']}%
- Wind: {current['wind']['speed_kph']} km/h {current['wind']['direction']}
- UV Index: {current['uv_index']}
- Visibility: {current['visibility_km']} km
- Pressure: {env['pressure_mb']} mb
- Time of day: {'Daytime' if env['is_daytime'] else 'Nighttime'}
- Precipitation: {env['precipitation_mm']} mm

"""
        
        # Add conversation history for context
        if self.conversation_history:
            prompt += "RECENT CONVERSATION:\n"
            for entry in self.conversation_history[-3:]:  # Last 3 exchanges
                prompt += f"User: {entry['user_message']}\n"
                prompt += f"Addy: {entry['ai_response'][:100]}...\n\n"
        
        # Add current user message
        prompt += f"""
CURRENT USER MESSAGE: "{message}"
LOCATION CONTEXT: {location or 'Not specified'}

Please respond as Addy, the friendly weather assistant. Use the weather data to provide specific, helpful advice. Be conversational and include relevant emojis. If the user asks about weather, incorporate the current conditions. If they ask for recommendations, use the actual weather data to give practical suggestions.

Response:"""
        
        return prompt
    
    def _fallback_response(self, message: str, location: Optional[str]) -> Dict:
        """Fallback response when AI is unavailable"""
        responses = {
            "weather": f"I'd love to help with weather information for {location or 'your area'}! However, my AI capabilities are currently limited. I can still provide basic weather data though.",
            "hello": "Hello! I'm Addy, your weather assistant. While my advanced AI features aren't fully active right now, I'm still here to help with weather information!",
            "help": "I can help you with:\n• Current weather conditions\n• Weather forecasts\n• Basic recommendations\n• Location-based weather data\n\nWhat would you like to know?",
            "default": f"Thanks for your message: '{message}'. I'm Addy, your weather assistant. My AI is currently in basic mode, but I can still help with weather data!"
        }
        
        message_lower = message.lower()
        if any(word in message_lower for word in ['weather', 'temperature', 'rain', 'sunny']):
            response_text = responses["weather"]
        elif any(word in message_lower for word in ['hello', 'hi', 'hey']):
            response_text = responses["hello"]
        elif any(word in message_lower for word in ['help', 'what', 'how']):
            response_text = responses["help"]
        else:
            response_text = responses["default"]
        
        return {
            "status": "success",
            "response": response_text,
            "ai_powered": False,
            "location": location
        }
    
    def get_conversation_summary(self) -> Dict:
        """Get summary of conversation history"""
        return {
            "total_exchanges": len(self.conversation_history),
            "recent_topics": [entry["user_message"][:50] for entry in self.conversation_history[-5:]],
            "locations_discussed": list(set([entry.get("location") for entry in self.conversation_history if entry.get("location")]))
        }

# Create global AI agent instance
ai_addy = FullAIAddyAgent()

async def chat_with_ai_addy(message: str, location: Optional[str] = None) -> Dict:
    """Enhanced AI chat function"""
    
    # Get weather data if location is provided
    weather_data = None
    if location:
        from weather_tool import fetch_weather_data
        weather_data = fetch_weather_data(location)
    
    # Chat with AI agent
    return await ai_addy.chat(message, location, weather_data)

def get_ai_capabilities() -> Dict:
    """Get current AI capabilities status"""
    return {
        "ai_available": GEMINI_AVAILABLE,
        "agent_name": ai_addy.name,
        "version": ai_addy.version,
        "features": [
            "Conversational AI responses",
            "Context-aware discussions", 
            "Weather-integrated advice",
            "Personality-driven interactions",
            "Conversation memory",
            "Adaptive recommendations"
        ] if GEMINI_AVAILABLE else ["Basic responses"],
        "conversation_history": len(ai_addy.conversation_history)
    }