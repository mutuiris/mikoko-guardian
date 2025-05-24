import datetime
import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
import requests

# Handle imports properly
try:
    from .config import Config
    from .weather_tool import fetch_weather_data, get_weather_forecast
except ImportError:
    from config import Config
    from weather_tool import fetch_weather_data, get_weather_forecast

@dataclass
class WeatherInsight:
    """Weather insight data structure"""
    comfort_level: str
    recommendations: List[str]
    activities: List[str]
    alerts: List[str]
    summary: str
    air_quality_info: Optional[Dict] = None

class EnhancedAddyAgent:
    """Enhanced Addy Weather Agent with comprehensive analysis"""
    
    def __init__(self):
        self.name = "Addy"
        self.version = "2.0"
        self.capabilities = [
            "Real-time weather analysis",
            "Activity recommendations", 
            "Weather alerts",
            "Air quality monitoring",
            "Multi-day forecasting",
            "Location-based insights",
            "Weather pattern analysis"
        ]
    
    def analyze_weather_comprehensive(self, weather_data: Dict) -> WeatherInsight:
        """
        Comprehensive weather analysis using WeatherAPI data
        
        Args:
            weather_data: Complete weather data from fetch_weather_data
            
        Returns:
            WeatherInsight: Detailed analysis and recommendations
        """
        try:
            # Extract key metrics
            current = weather_data["current_conditions"]
            condition = weather_data["weather_condition"]
            environment = weather_data["environmental_indicators"]
            location = weather_data["location"]
            
            temp = current["temperature_celsius"]
            humidity = current["humidity_percent"]
            wind_speed = current["wind"]["speed_kph"]
            condition_text = condition["description"].lower()
            is_day = environment["is_daytime"]
            precipitation = environment["precipitation_mm"]
            uv_index = current["uv_index"]
            pressure = environment["pressure_mb"]
            
            # Analyze comfort level
            comfort_level = self._calculate_comfort_index(temp, humidity, wind_speed, uv_index)
            
            # Generate intelligent recommendations
            recommendations = self._generate_smart_recommendations(
                temp, humidity, wind_speed, condition_text, precipitation, uv_index, is_day
            )
            
            # Suggest location-specific activities
            activities = self._suggest_contextual_activities(
                temp, condition_text, wind_speed, is_day, location["name"]
            )
            
            # Check for weather alerts
            alerts = self._assess_weather_warnings(
                temp, wind_speed, condition_text, precipitation, uv_index, pressure
            )
            
            # Create intelligent summary
            summary = self._create_intelligent_summary(
                weather_data, comfort_level, is_day
            )
            
            # Analyze air quality if available
            air_quality_info = None
            if "air_quality" in weather_data:
                air_quality_info = self._analyze_air_quality(weather_data["air_quality"])
            
            return WeatherInsight(
                comfort_level=comfort_level,
                recommendations=recommendations,
                activities=activities,
                alerts=alerts,
                summary=summary,
                air_quality_info=air_quality_info
            )
            
        except Exception as e:
            return WeatherInsight(
                comfort_level="Unknown",
                recommendations=[f"Analysis error: {str(e)}"],
                activities=[],
                alerts=[],
                summary="Unable to analyze current weather conditions"
            )
    
    def _calculate_comfort_index(self, temp: float, humidity: float, wind: float, uv: float) -> str:
        """Calculate comprehensive comfort index"""
        
        # Temperature comfort (0-4 scale)
        if 20 <= temp <= 25:
            temp_score = 4
        elif 18 <= temp <= 28:
            temp_score = 3
        elif 15 <= temp <= 32:
            temp_score = 2
        elif 10 <= temp <= 35:
            temp_score = 1
        else:
            temp_score = 0
        
        # Humidity comfort (0-4 scale)
        if 40 <= humidity <= 60:
            humidity_score = 4
        elif 30 <= humidity <= 70:
            humidity_score = 3
        elif 20 <= humidity <= 80:
            humidity_score = 2
        elif 10 <= humidity <= 90:
            humidity_score = 1
        else:
            humidity_score = 0
        
        # Wind comfort (0-4 scale)
        if wind < 10:
            wind_score = 4
        elif wind < 20:
            wind_score = 3
        elif wind < 30:
            wind_score = 2
        elif wind < 40:
            wind_score = 1
        else:
            wind_score = 0
        
        # UV comfort (0-4 scale)
        if uv <= 2:
            uv_score = 4
        elif uv <= 5:
            uv_score = 3
        elif uv <= 7:
            uv_score = 2
        elif uv <= 10:
            uv_score = 1
        else:
            uv_score = 0
        
        # Calculate overall comfort (weighted average)
        overall_score = (temp_score * 0.4 + humidity_score * 0.25 + 
                        wind_score * 0.25 + uv_score * 0.1)
        
        if overall_score >= 3.5:
            return "Excellent"
        elif overall_score >= 3.0:
            return "Very Good"
        elif overall_score >= 2.5:
            return "Good"
        elif overall_score >= 2.0:
            return "Fair"
        elif overall_score >= 1.0:
            return "Poor"
        else:
            return "Very Poor"
    
    def _generate_smart_recommendations(self, temp: float, humidity: float, 
                                      wind: float, condition: str, precip: float, 
                                      uv: float, is_day: bool) -> List[str]:
        """Generate context-aware recommendations"""
        recommendations = []
        
        # Temperature-based recommendations
        if temp > 35:
            recommendations.extend([
                "🌡️ Extreme heat warning - avoid outdoor activities 11am-4pm",
                "💧 Drink water every 15-20 minutes, even if not thirsty",
                "🏠 Seek air-conditioned spaces when possible"
            ])
        elif temp > 30:
            recommendations.extend([
                "☀️ Hot weather - wear light, loose-fitting clothing",
                "🧴 Apply sunscreen SPF 30+ every 2 hours",
                "🌳 Take breaks in shade during outdoor activities"
            ])
        elif temp < 5:
            recommendations.extend([
                "🧥 Very cold - dress in warm layers",
                "🧤 Protect extremities from frostbite",
                "☕ Warm beverages help maintain body temperature"
            ])
        elif temp < 15:
            recommendations.extend([
                "🧥 Cool weather - light jacket recommended",
                "🍵 Perfect weather for hot beverages"
            ])
        
        # Humidity recommendations
        if humidity > 80:
            recommendations.append("💧 High humidity - stay hydrated and cool")
        elif humidity < 30:
            recommendations.append("🌵 Low humidity - use moisturizer for skin/lips")
        
        # Wind recommendations
        if wind > 30:
            recommendations.extend([
                "💨 Strong winds - secure loose outdoor items",
                "🚗 Drive carefully - crosswinds may affect vehicles"
            ])
        elif wind > 20:
            recommendations.append("🍃 Moderate winds - great for kite flying!")
        
        # UV recommendations
        if uv >= 8:
            recommendations.extend([
                "🕶️ Very high UV - sunglasses and hat essential",
                "🧴 SPF 50+ sunscreen required"
            ])
        elif uv >= 6:
            recommendations.append("☀️ High UV - sun protection recommended")
        elif uv >= 3:
            recommendations.append("🕶️ Moderate UV - sunglasses suggested")
        
        # Precipitation recommendations
        if precip > 10:
            recommendations.extend([
                "☔ Heavy rain expected - waterproof gear essential",
                "🚗 Driving conditions may be hazardous"
            ])
        elif precip > 2:
            recommendations.append("🌧️ Light rain possible - carry umbrella")
        
        # Condition-specific recommendations
        if "thunderstorm" in condition or "storm" in condition:
            recommendations.extend([
                "⛈️ Thunderstorms - stay indoors",
                "📱 Avoid using electronic devices outdoors"
            ])
        elif "fog" in condition or "mist" in condition:
            recommendations.extend([
                "🌫️ Reduced visibility - drive with headlights",
                "🚶 Be extra careful when walking"
            ])
        elif "snow" in condition:
            recommendations.extend([
                "❄️ Snow conditions - drive slowly and carefully",
                "🧤 Dress warmly and wear appropriate footwear"
            ])
        
        return recommendations
    
    def _suggest_contextual_activities(self, temp: float, condition: str, 
                                     wind: float, is_day: bool, location: str) -> List[str]:
        """Suggest activities based on weather and location context"""
        activities = []
        time_period = "daytime" if is_day else "evening"
        
        # Temperature-based activities
        if temp >= 25 and "rain" not in condition and "storm" not in condition:
            activities.extend([
                f"🏊 Swimming or water sports ({time_period})",
                f"🏖️ Beach activities ({time_period})",
                f"🍦 Outdoor ice cream or cold drinks",
                f"🌳 Picnic in the park"
            ])
        elif 20 <= temp < 25:
            activities.extend([
                f"🚶 Walking or light hiking ({time_period})",
                f"🚴 Cycling ({time_period})",
                f"⚽ Outdoor sports",
                f"📸 Photography walks"
            ])
        elif 15 <= temp < 20:
            activities.extend([
                f"☕ Outdoor café visits ({time_period})",
                f"🛍️ Shopping and sightseeing",
                f"🎨 Outdoor sketching or painting"
            ])
        elif 10 <= temp < 15:
            activities.extend([
                f"🏛️ Museum visits ({time_period})",
                f"📚 Library or bookstore browsing",
                f"🎬 Movie theater visits"
            ])
        else:
            activities.extend([
                f"🏠 Indoor activities recommended",
                f"🧘 Indoor yoga or meditation",
                f"🍳 Cooking or baking"
            ])
        
        # Weather condition activities
        if "clear" in condition or "sunny" in condition:
            activities.extend([
                "📸 Perfect lighting for photography",
                "🌻 Garden visits or outdoor markets"
            ])
        elif "cloudy" in condition and "rain" not in condition:
            activities.extend([
                "🎨 Great diffused lighting for art",
                "🏛️ Outdoor architecture tours"
            ])
        elif "rain" in condition:
            activities.extend([
                "☔ Cozy indoor activities",
                "📚 Reading by the window",
                "🎵 Indoor music or podcasts"
            ])
        
        # Location-specific suggestions (basic examples)
        location_lower = location.lower()
        if any(coastal in location_lower for coastal in ['mombasa', 'miami', 'sydney', 'barcelona']):
            if temp >= 20:
                activities.append("🌊 Beach walks or water activities")
        elif any(mountain in location_lower for mountain in ['nairobi', 'denver', 'zurich']):
            activities.append("🏔️ Mountain views and highland activities")
        
        return activities[:6]  # Limit to 6 suggestions
    
    def _assess_weather_warnings(self, temp: float, wind: float, condition: str, 
                               precip: float, uv: float, pressure: float) -> List[str]:
        """Assess and generate weather warnings"""
        alerts = []
        
        # Temperature alerts
        if temp > 40:
            alerts.append("🚨 EXTREME HEAT WARNING - Serious health risk!")
        elif temp > 35:
            alerts.append("🌡️ HEAT ADVISORY - High risk of heat exhaustion")
        elif temp < -10:
            alerts.append("🧊 EXTREME COLD WARNING - Frostbite risk!")
        elif temp < 0:
            alerts.append("❄️ FREEZING ALERT - Ice formation likely")
        
        # Wind alerts
        if wind > 50:
            alerts.append("🌪️ SEVERE WIND WARNING - Dangerous conditions!")
        elif wind > 40:
            alerts.append("💨 HIGH WIND WARNING - Secure loose objects")
        elif wind > 30:
            alerts.append("🍃 WIND ADVISORY - Use caution outdoors")
        
        # Precipitation alerts
        if precip > 25:
            alerts.append("🌊 FLOOD WARNING - Heavy rainfall, avoid low areas")
        elif precip > 15:
            alerts.append("☔ HEAVY RAIN WARNING - Reduced visibility")
        elif precip > 5:
            alerts.append("🌧️ RAIN ADVISORY - Slippery conditions")
        
        # UV alerts
        if uv >= 11:
            alerts.append("☀️ EXTREME UV WARNING - Avoid sun exposure")
        elif uv >= 8:
            alerts.append("🕶️ HIGH UV ALERT - Sun protection essential")
        
        # Pressure alerts (basic)
        if pressure < 980:
            alerts.append("📉 LOW PRESSURE - Weather changes likely")
        elif pressure > 1040:
            alerts.append("📈 HIGH PRESSURE - Stable weather expected")
        
        # Condition-specific alerts
        if "thunderstorm" in condition:
            alerts.append("⛈️ THUNDERSTORM ALERT - Seek shelter immediately")
        elif "tornado" in condition:
            alerts.append("🌪️ TORNADO WARNING - Take cover now!")
        elif "blizzard" in condition:
            alerts.append("❄️ BLIZZARD WARNING - Do not travel")
        elif "fog" in condition and "dense" in condition:
            alerts.append("🌫️ DENSE FOG ADVISORY - Severely reduced visibility")
        
        return alerts
    
    def _analyze_air_quality(self, air_quality: Dict) -> Dict:
        """Analyze air quality data"""
        try:
            aqi_us = air_quality.get("us_epa_index", 0)
            
            if aqi_us >= 5:
                level = "Hazardous"
                advice = "Health emergency - everyone avoid outdoor activities"
            elif aqi_us >= 4:
                level = "Unhealthy"
                advice = "Everyone should limit outdoor activities"
            elif aqi_us >= 3:
                level = "Unhealthy for Sensitive Groups"
                advice = "Sensitive groups should limit outdoor activities"
            elif aqi_us >= 2:
                level = "Moderate"
                advice = "Generally acceptable air quality"
            else:
                level = "Good"
                advice = "Excellent air quality for outdoor activities"
            
            return {
                "level": level,
                "advice": advice,
                "us_aqi": aqi_us,
                "pm2_5": air_quality.get("pm2_5_μgm3", "N/A"),
                "pm10": air_quality.get("pm10_μgm3", "N/A")
            }
            
        except Exception:
            return {"level": "Unknown", "advice": "Air quality data unavailable"}
    
    def _create_intelligent_summary(self, weather_data: Dict, comfort: str, is_day: bool) -> str:
        """Create an intelligent, conversational weather summary"""
        location = weather_data["location"]["name"]
        temp = weather_data["current_conditions"]["temperature_celsius"]
        condition = weather_data["weather_condition"]["description"]
        humidity = weather_data["current_conditions"]["humidity_percent"]
        wind = weather_data["current_conditions"]["wind"]["speed_kph"]
        
        time_context = "during the day" if is_day else "this evening"
        
        # Create engaging summary
        summary = f"Weather in {location} {time_context}: {condition} with {temp}°C. "
        
        # Add comfort assessment
        if comfort == "Excellent":
            summary += "Perfect conditions for any outdoor plans! "
        elif comfort == "Very Good":
            summary += "Great weather for outdoor activities. "
        elif comfort == "Good":
            summary += "Pleasant conditions overall. "
        elif comfort == "Fair":
            summary += "Acceptable weather with minor discomfort. "
        else:
            summary += "Challenging conditions - plan accordingly. "
        
        # Add specific details
        if humidity > 80:
            summary += f"It's quite humid at {humidity}%. "
        elif humidity < 30:
            summary += f"Very dry air at {humidity}% humidity. "
        
        if wind > 20:
            summary += f"Breezy conditions with {wind} km/h winds. "
        elif wind < 5:
            summary += "Very calm with minimal wind. "
        
        return summary.strip()
    
    def get_conversation_response(self, message: str, location: Optional[str] = None) -> Dict:
        """
        Generate intelligent conversational responses about weather
        
        Args:
            message: User's message
            location: Location context
            
        Returns:
            Dict: Comprehensive response with analysis
        """
        try:
            message_lower = message.lower()
            
            # Determine if weather data is needed
            weather_keywords = ['weather', 'temperature', 'rain', 'sunny', 'cloudy', 'wind', 'humidity', 'forecast']
            needs_weather = any(keyword in message_lower for keyword in weather_keywords)
            
            if needs_weather and location:
                # Get weather data
                weather_result = fetch_weather_data(location)
                if weather_result["status"] == "success":
                    # Perform comprehensive analysis
                    analysis = self.analyze_weather_comprehensive(weather_result)
                    
                    # Generate contextual response
                    response = f"Hi! I'm Addy, your weather assistant. {analysis.summary}\n\n"
                    
                    if analysis.recommendations:
                        response += "💡 **Recommendations:**\n"
                        for rec in analysis.recommendations[:3]:
                            response += f"• {rec}\n"
                    
                    if analysis.activities:
                        response += f"\n🎯 **Perfect for:**\n"
                        for activity in analysis.activities[:3]:
                            response += f"• {activity}\n"
                    
                    if analysis.alerts:
                        response += f"\n⚠️ **Weather Alerts:**\n"
                        for alert in analysis.alerts:
                            response += f"• {alert}\n"
                    
                    if analysis.air_quality_info:
                        aqi = analysis.air_quality_info
                        response += f"\n🌬️ **Air Quality:** {aqi['level']} - {aqi['advice']}"
                    
                    return {
                        "status": "success",
                        "response": response.strip(),
                        "analysis": analysis.__dict__,
                        "location": location
                    }
                else:
                    return {
                        "status": "error",
                        "response": f"I couldn't get weather data for {location}. Please check the location name and try again.",
                        "location": location
                    }
            else:
                # General conversation response
                responses = [
                    "Hello! I'm Addy, your weather assistant. Ask me about weather in any city!",
                    "Hi there! I can help you with weather information, forecasts, and activity recommendations.",
                    "Hey! I'm here to help with all your weather questions. Try asking about weather in your city!",
                    "Greetings! I provide weather data, analysis, and recommendations. What would you like to know?"
                ]
                
                import random
                return {
                    "status": "success",
                    "response": random.choice(responses),
                    "location": location
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error_message": f"Error generating response: {str(e)}"
            }

# Create global enhanced agent instance
enhanced_addy = EnhancedAddyAgent()

def chat_with_enhanced_addy(message: str, location: Optional[str] = None) -> Dict:
    """Enhanced chat function with comprehensive analysis"""
    return enhanced_addy.get_conversation_response(message, location)

def get_enhanced_weather_analysis(location: str) -> Dict:
    """Get comprehensive weather analysis for a location"""
    weather_data = fetch_weather_data(location)
    if weather_data["status"] == "success":
        analysis = enhanced_addy.analyze_weather_comprehensive(weather_data)
        return {
            "status": "success",
            "analysis": analysis.__dict__,
            "weather_data": weather_data
        }
    return weather_data