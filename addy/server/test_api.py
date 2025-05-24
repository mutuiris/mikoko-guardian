import requests
import json

def test_api_endpoints():
    """Test the API endpoints"""
    base_url = "http://localhost:8000"
    
    print("Testing API endpoints...")
    print("-" * 40)
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/api/health")
        print(f"Health endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Health endpoint error: {e}")
    
    print("-" * 40)
    
    # Test weather endpoint
    try:
        response = requests.get(f"{base_url}/api/weather/simple/Nairobi")
        print(f"Weather endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Location: {data['location']['name']}")
            print(f"Temperature: {data['current']['temp_c']}°C")
            print(f"Condition: {data['current']['condition']['text']}")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Weather endpoint error: {e}")

if __name__ == "__main__":
    test_api_endpoints()