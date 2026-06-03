import requests
from typing import Dict, Optional
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_weather_by_city(city: str, api_key: str, units: str = "metric") -> Dict:
    """
    Get current weather for a city using OpenWeatherMap API.
    
    Args:
        city (str): Name of the city (e.g., "Bangalore", "New York")
        api_key (str): Your OpenWeatherMap API key
        units (str): "metric" (Celsius), "imperial" (Fahrenheit), or "standard" (Kelvin)
    
    Returns:
        dict: Weather information or error message
    """
    
    # Step 1: Get coordinates from city name (Geocoding)
    geo_url = "http://api.openweathermap.org/geo/1.0/direct"
    geo_params = {
        "q": city,
        "limit": 1,
        "appid": api_key
    }
    
    try:
        geo_response = requests.get(geo_url, params=geo_params)
        geo_response.raise_for_status()
        geo_data = geo_response.json()
        
        if not geo_data:
            return {"error": f"City '{city}' not found."}
        
        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]
        city_name = geo_data[0]["name"]
        country = geo_data[0].get("country", "")
        
        # Step 2: Get weather data using coordinates
        weather_url = "https://api.openweathermap.org/data/2.5/weather"
        weather_params = {
            "lat": lat,
            "lon": lon,
            "appid": api_key,
            "units": units
        }
        
        weather_response = requests.get(weather_url, params=weather_params)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        
        # Extract useful information
        weather_info = {
            "city": f"{city_name}, {country}",
            "temperature": weather_data["main"]["temp"],
            "feels_like": weather_data["main"]["feels_like"],
            "humidity": weather_data["main"]["humidity"],
            "description": weather_data["weather"][0]["description"].capitalize(),
            "wind_speed": weather_data["wind"]["speed"],
            "pressure": weather_data["main"]["pressure"],
            "visibility": weather_data.get("visibility", 0) / 1000,  # in km
            "icon": weather_data["weather"][0]["icon"],
        }
        
        return weather_info
        
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}
    except (KeyError, IndexError) as e:
        return {"error": "Failed to parse weather data."}


if __name__ == "__main__":
    
    city = input("Enter city name: ").strip()
    
    if city:
        result = get_weather_by_city(city, API_KEY)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"\n🌤 Weather in {result['city']}:")
            print(f"Temperature: {result['temperature']}°C")
            print(f"Feels like: {result['feels_like']}°C")
            print(f"Condition: {result['description']}")
            print(f"Humidity: {result['humidity']}%")
            print(f"Wind Speed: {result['wind_speed']} m/s")
            print(f"Pressure: {result['pressure']} hPa")