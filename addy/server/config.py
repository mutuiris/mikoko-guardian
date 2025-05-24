import os
from typing import Optional
from pathlib import Path

def load_env_file(env_path: Optional[str] = None) -> None:
    """
    Load environment variables from .env file
    
    Args:
        env_path (Optional[str]): Path to .env file. If None, looks in parent directory.
    """
    if env_path is None:
        # Look for .env file in the addy directory (parent of server)
        current_dir = Path(__file__).parent
        env_path = current_dir.parent / '.env'
    
    env_file = Path(env_path)
    
    if not env_file.exists():
        print(f"Warning: .env file not found at {env_file}")
        return
    
    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    os.environ[key] = value
        print(f"Environment variables loaded from {env_file}")
    except Exception as e:
        print(f"Error loading .env file: {e}")

# Load environment variables when module is imported
load_env_file()

class Config:
    """Configuration class for environment variables"""
    
    # Weather API Configuration
    WEATHER_API_KEY: str = os.getenv('WEATHER_API_KEY', '')
    WEATHER_API_BASE_URL: str = os.getenv('WEATHER_API_BASE_URL', 'https://api.weatherapi.com/v1/current.json')
    WEATHER_FORECAST_URL: str = os.getenv('WEATHER_FORECAST_URL', 'https://api.weatherapi.com/v1/forecast.json')
    
    # Google AI Configuration
    GOOGLE_API_KEY: str = os.getenv('GOOGLE_API_KEY', '')
    GOOGLE_GENAI_USE_VERTEXAI: bool = os.getenv('GOOGLE_GENAI_USE_VERTEXAI', 'false').lower() == 'true'
    
    # Application Configuration
    APP_NAME: str = os.getenv('APP_NAME', 'Addy Weather Monitor')
    APP_VERSION: str = os.getenv('APP_VERSION', '1.0.0')
    DEBUG_MODE: bool = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    
    # API Configuration
    API_TIMEOUT_SECONDS: int = int(os.getenv('API_TIMEOUT_SECONDS', '10'))
    MAX_FORECAST_DAYS: int = int(os.getenv('MAX_FORECAST_DAYS', '10'))
    
    @classmethod
    def validate_config(cls) -> bool:
        """
        Validate that required environment variables are set
        
        Returns:
            bool: True if all required variables are set
        """
        required_vars = [
            ('WEATHER_API_KEY', cls.WEATHER_API_KEY),
            ('GOOGLE_API_KEY', cls.GOOGLE_API_KEY)
        ]
        
        missing_vars = []
        for var_name, var_value in required_vars:
            if not var_value:
                missing_vars.append(var_name)
        
        if missing_vars:
            print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
            return False
        
        return True
    
    @classmethod
    def get_config_info(cls) -> dict:
        """
        Get configuration information (excluding sensitive data)
        
        Returns:
            dict: Configuration information
        """
        return {
            "app_name": cls.APP_NAME,
            "app_version": cls.APP_VERSION,
            "debug_mode": cls.DEBUG_MODE,
            "api_timeout": cls.API_TIMEOUT_SECONDS,
            "max_forecast_days": cls.MAX_FORECAST_DAYS,
            "weather_api_configured": bool(cls.WEATHER_API_KEY),
            "google_api_configured": bool(cls.GOOGLE_API_KEY),
            "use_vertex_ai": cls.GOOGLE_GENAI_USE_VERTEXAI
        }