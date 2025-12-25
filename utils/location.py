import requests
from config import Config

class LocationAgent:
    def __init__(self):
        self.weather_api_key = Config.WEATHER_API_KEY
    
    def get_location_from_ip(self, ip_address=None):
        """Get location from IP address using ip-api.com (free)"""
        try:
            url = f"http://ip-api.com/json/{ip_address}" if ip_address else "http://ip-api.com/json/"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if data['status'] == 'success':
                return {
                    'city': data.get('city'),
                    'region': data.get('regionName'),
                    'country': data.get('country'),
                    'lat': data.get('lat'),
                    'lon': data.get('lon'),
                    'timezone': data.get('timezone'),
                    'zip': data.get('zip', '')
                }
        except Exception as e:
            print(f"Error getting location: {e}")
        
        # Default location if detection fails
        return {
            'city': 'Unknown',
            'region': 'Unknown',
            'country': 'India',
            'lat': 20.5937,
            'lon': 78.9629,
            'timezone': 'Asia/Kolkata',
            'zip': ''
        }
    
    def get_weather(self, lat, lon):
        """Get weather data from OpenWeatherMap"""
        if not self.weather_api_key:
            return self.get_weather_free(lat, lon)
        
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.weather_api_key,
                'units': 'metric'
            }
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            return {
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'],
                'wind_speed': data['wind']['speed'],
                'pressure': data['main']['pressure'],
                'rain': data.get('rain', {}).get('1h', 0)
            }
        except Exception as e:
            print(f"Error getting weather: {e}")
            return self.get_weather_free(lat, lon)
    
    def get_weather_free(self, lat, lon):
        """Fallback weather using free API"""
        try:
            url = f"https://api.open-meteo.com/v1/forecast"
            params = {
                'latitude': lat,
                'longitude': lon,
                'current_weather': True,
                'hourly': 'temperature_2m,relative_humidity_2m,precipitation'
            }
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            current = data['current_weather']
            
            return {
                'temperature': current['temperature'],
                'feels_like': current['temperature'],
                'humidity': data['hourly']['relative_humidity_2m'][0],
                'description': self.weather_code_to_desc(current['weathercode']),
                'wind_speed': current['windspeed'],
                'pressure': 1013,  # Standard pressure
                'rain': data['hourly']['precipitation'][0]
            }
        except Exception as e:
            print(f"Error with free weather: {e}")
            return {
                'temperature': 25,
                'feels_like': 25,
                'humidity': 60,
                'description': 'Partly cloudy',
                'wind_speed': 5,
                'pressure': 1013,
                'rain': 0
            }
    
    def weather_code_to_desc(self, code):
        """Convert weather code to description"""
        codes = {
            0: 'Clear sky',
            1: 'Mainly clear',
            2: 'Partly cloudy',
            3: 'Overcast',
            45: 'Foggy',
            61: 'Light rain',
            63: 'Moderate rain',
            65: 'Heavy rain',
            80: 'Rain showers'
        }
        return codes.get(code, 'Unknown')