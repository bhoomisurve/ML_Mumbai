import google.generativeai as genai
from config import Config
import logging

logger = logging.getLogger(__name__)

class GardenKnowledgeAgent:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def get_plant_care_guide(self, plant_name, location, climate_data, language='en'):
        """
        Get comprehensive care guide for specific plant
        """
        try:
            prompt = f"""You are an expert home gardening advisor in India.

Plant: {plant_name}
Location: {location}
Current Temperature: {climate_data.get('current', {}).get('temperature', 'unknown')}°C
Humidity: {climate_data.get('current', {}).get('humidity', 'unknown')}%

Provide a comprehensive home gardening guide including:

1. **Ideal Growing Conditions**: Sunlight, water, soil type for home gardens
2. **Watering Schedule**: How often and how much (for pots/containers and ground)
3. **Fertilization**: Organic options (compost, kitchen waste, natural fertilizers)
4. **Common Problems**: Pests and diseases specific to this plant in Indian climate
5. **Seasonal Care**: Tips for different seasons (monsoon, summer, winter)
6. **Container Growing**: Pot size, soil mix if growing in containers
7. **Companion Plants**: What grows well alongside this plant
8. **Harvest Tips**: When and how to harvest (if applicable)
9. **Urban Gardening Tips**: Balcony/terrace/small space growing advice

Language: {language}

Provide practical, actionable advice for beginners. Keep it simple and encouraging!"""

            response = self.model.generate_content(prompt)
            return {
                'plant_name': plant_name,
                'care_guide': response.text,
                'language': language
            }
            
        except Exception as e:
            logger.error(f"Care guide generation failed: {str(e)}")
            return {'error': True, 'message': str(e)}
    
    def get_disease_treatment(self, disease_name, plant_name, language='en'):
        """
        Get organic treatment options for plant diseases
        """
        try:
            prompt = f"""You are an organic gardening expert in India.

Plant: {plant_name}
Disease/Problem: {disease_name}

Provide home remedies and organic treatment options:

1. **Identification Confirmation**: How to confirm this is the correct diagnosis
2. **Organic Treatments**: Home remedies using kitchen ingredients (neem, turmeric, garlic, etc.)
3. **Cultural Practices**: Changes in watering, pruning, or care
4. **Prevention**: How to prevent recurrence
5. **When to Use Chemicals**: Only as last resort, with minimal safe dosage
6. **Recovery Timeline**: How long until improvement

Language: {language}

Focus on safe, accessible, organic solutions for home gardeners. Avoid toxic chemicals unless absolutely necessary.

Format as JSON with keys: confirmation_signs, organic_remedies (array), cultural_practices (array), prevention_tips (array), recovery_time, chemical_option_if_needed"""

            response = self.model.generate_content(prompt)
            return self._parse_treatment_response(response.text, disease_name)
            
        except Exception as e:
            logger.error(f"Treatment guide generation failed: {str(e)}")
            return {'error': True, 'message': str(e)}
    
    def _parse_treatment_response(self, response_text, disease_name):
        """Parse treatment response"""
        try:
            import json
            import re
            
            json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(1))
                data['disease_name'] = disease_name
                return data
            
            return json.loads(response_text)
            
        except:
            return {
                'disease_name': disease_name,
                'treatment_text': response_text,
                'raw_response': True
            }