import requests
from config import Config
import logging

logger = logging.getLogger(__name__)

class WeatherAgent:
    def __init__(self):
        self.api_key = Config.WEATHER_API_KEY
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    def get_weather_forecast(self, lat, lon):
        """
        Get 5-day weather forecast for gardening decisions
        """
        try:
            # Current weather
            current_url = f"{self.base_url}/weather"
            current_params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            current_response = requests.get(current_url, params=current_params)
            current_data = current_response.json()
            
            # 5-day forecast
            forecast_url = f"{self.base_url}/forecast"
            forecast_params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            forecast_response = requests.get(forecast_url, params=forecast_params)
            forecast_data = forecast_response.json()
            
            return self._format_weather_data(current_data, forecast_data)
            
        except Exception as e:
            logger.error(f"Weather fetch failed: {str(e)}")
            return {'error': True, 'message': 'Weather data unavailable'}
    
    def _format_weather_data(self, current, forecast):
        """Format weather data for gardening context"""
        try:
            # Calculate rainfall probability
            rain_forecast = [
                item for item in forecast['list'][:8]  # Next 24 hours
                if 'rain' in item
            ]
            
            return {
                'current': {
                    'temperature': current['main']['temp'],
                    'humidity': current['main']['humidity'],
                    'description': current['weather'][0]['description'],
                    'wind_speed': current['wind']['speed']
                },
                'forecast': {
                    'will_rain': len(rain_forecast) > 0,
                    'rain_probability': len(rain_forecast) / 8 * 100,
                    'avg_temp_3day': sum(
                        item['main']['temp'] 
                        for item in forecast['list'][:24]
                    ) / 24,
                    'conditions': [
                        {
                            'time': item['dt_txt'],
                            'temp': item['main']['temp'],
                            'humidity': item['main']['humidity'],
                            'rain': item.get('rain', {}).get('3h', 0)
                        }
                        for item in forecast['list'][:8]
                    ]
                },
                'gardening_advice': self._generate_weather_advice(current, rain_forecast)
            }
        except Exception as e:
            logger.error(f"Weather formatting failed: {str(e)}")
            return {}
    
    def _generate_weather_advice(self, current, rain_forecast):
        """Generate gardening advice based on weather"""
        advice = []
        
        temp = current['main']['temp']
        humidity = current['main']['humidity']
        
        if temp > 35:
            advice.append("🌡️ Very hot! Water plants early morning or evening. Provide shade.")
        elif temp < 10:
            advice.append("❄️ Cold weather! Protect sensitive plants. Reduce watering.")
        
        if humidity > 80:
            advice.append("💧 High humidity! Watch for fungal diseases. Ensure good air circulation.")
        elif humidity < 30:
            advice.append("🏜️ Low humidity! Mist plants. Check soil moisture frequently.")
        
        if len(rain_forecast) > 0:
            advice.append("🌧️ Rain expected! Skip watering. Check drainage.")
        else:
            advice.append("☀️ No rain forecast. Maintain regular watering schedule.")
        
        return advice