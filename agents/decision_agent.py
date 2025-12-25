import google.generativeai as genai
from config import Config
import json

class DecisionAgent:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def generate_recommendations(self, detection_result, weather_data, location, language='en'):
        """Generate comprehensive gardening recommendations using Gemini"""
        
        crop = detection_result.get('crop', 'unknown')
        disease = detection_result.get('disease', 'Unknown')
        confidence = detection_result.get('confidence', 0) * 100
        is_healthy = detection_result.get('is_healthy', False)
        
        prompt = f"""You are an expert gardening advisor helping home gardeners and urban farmers in India.

DETECTION RESULTS:
- Crop/Plant: {crop.title()}
- Health Status: {"Healthy ✓" if is_healthy else f"Disease Detected: {disease}"}
- Confidence: {confidence:.1f}%

LOCATION & WEATHER:
- Location: {location.get('city')}, {location.get('region')}, {location.get('country')}
- Temperature: {weather_data.get('temperature')}°C (Feels like {weather_data.get('feels_like')}°C)
- Humidity: {weather_data.get('humidity')}%
- Weather: {weather_data.get('description')}
- Wind Speed: {weather_data.get('wind_speed')} m/s
- Recent Rainfall: {weather_data.get('rain', 0)}mm

TARGET AUDIENCE: Home gardeners, balcony gardeners, urban farmers with limited space

INSTRUCTIONS:
1. Provide practical, actionable gardening advice suitable for home/urban settings
2. Focus on organic and sustainable methods
3. Include specific dosage recommendations (e.g., "1 tablespoon per liter")
4. Consider the current weather conditions
5. Give step-by-step guidance that's easy to follow
6. Recommend easily available materials from local garden stores
7. Include prevention tips for future growing
8. Response language: {"Hindi (हिंदी)" if language == 'hi' else "English"}

Please provide recommendations in the following JSON format:
{{
  "summary": "Brief 2-3 sentence overview in simple language",
  "disease_info": {{
    "name": "Disease name or 'Healthy Plant'",
    "severity": "Low/Medium/High or N/A",
    "description": "What is this condition and why it occurs"
  }},
  "immediate_actions": [
    "Specific action 1 with measurements",
    "Specific action 2 with timing",
    "Specific action 3"
  ],
  "treatment": {{
    "organic_solutions": [
      "Solution 1 with exact recipe/dosage",
      "Solution 2 with application method"
    ],
    "chemical_solutions": [
      "Product name with exact dosage",
      "Application frequency and timing"
    ],
    "application_schedule": "When and how often to apply"
  }},
  "watering": {{
    "frequency": "How often to water given current weather",
    "amount": "How much water per plant/pot",
    "timing": "Best time of day to water",
    "weather_note": "Adjustments based on current conditions"
  }},
  "fertilization": {{
    "type": "Recommended fertilizer type for home gardens",
    "dosage": "Exact amount per plant/pot",
    "frequency": "How often to fertilize",
    "organic_options": ["Option 1", "Option 2"]
  }},
  "environmental_care": {{
    "sunlight": "Hours needed and positioning",
    "temperature": "Optimal range and current suitability",
    "humidity": "Requirements and how to adjust",
    "spacing": "For container or small garden"
  }},
  "prevention_tips": [
    "Tip 1 for preventing this issue",
    "Tip 2 for general plant health",
    "Tip 3 for long-term care"
  ],
  "shopping_list": [
    "Item 1 needed from garden store",
    "Item 2 with quantity",
    "Item 3 (specify organic/chemical)"
  ],
  "timeline": "Expected recovery time or growth schedule",
  "warning_signs": [
    "Sign to watch for",
    "When to take additional action"
  ],
  "local_considerations": "Specific advice for {location.get('region')} region",
  "next_steps": "What to do after initial treatment"
}}

Provide ONLY the JSON output, no additional text."""

        try:
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            text = response.text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.endswith('```'):
                text = text[:-3]
            text = text.strip()
            
            recommendations = json.loads(text)
            return recommendations
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return self.get_fallback_recommendations(crop, disease, is_healthy)
    
    def get_fallback_recommendations(self, crop, disease, is_healthy):
        """Fallback recommendations if API fails"""
        return {
            "summary": f"Your {crop} plant {'appears healthy' if is_healthy else f'may have {disease}'}. Keep monitoring and maintain good care practices.",
            "disease_info": {
                "name": disease if not is_healthy else "Healthy Plant",
                "severity": "Unknown" if not is_healthy else "N/A",
                "description": "Unable to generate detailed analysis. Please consult local gardening expert."
            },
            "immediate_actions": [
                "Remove any affected leaves",
                "Ensure proper air circulation",
                "Check soil moisture"
            ],
            "treatment": {
                "organic_solutions": ["Neem oil spray", "Increase spacing between plants"],
                "chemical_solutions": ["Consult local garden store"],
                "application_schedule": "Follow product instructions"
            },
            "watering": {
                "frequency": "Check soil daily",
                "amount": "Water when top inch is dry",
                "timing": "Early morning",
                "weather_note": "Adjust based on weather"
            },
            "prevention_tips": [
                "Maintain good air circulation",
                "Avoid overhead watering",
                "Use quality potting mix"
            ]
        }
    
    def translate_text(self, text, target_language):
        """Translate text to target language"""
        if target_language == 'en':
            return text
        
        prompt = f"""Translate the following gardening advice to {Config.LANGUAGES[target_language]}. 
Maintain technical terms where appropriate and keep the practical nature of the advice.

Text to translate:
{text}

Provide only the translation, no additional text."""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            return text  # Return original if translation fails