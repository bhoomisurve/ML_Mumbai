import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # MongoDB Configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'garden_advisor')
    
    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')  # Optional: OpenWeatherMap
    
    # Upload Configuration
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    
    # Model Configuration
    MODEL_PATH = 'models'
    CROPS = ['apple', 'cherry', 'corn', 'grape', 'peach', 'pepper', 'potato', 'strawberry', 'tomato']
    
    # Supported Languages
    LANGUAGES = {
        'en': 'English',
        'hi': 'हिंदी (Hindi)',
        'ta': 'தமிழ் (Tamil)',
        'te': 'తెలుగు (Telugu)',
        'bn': 'বাংলা (Bengali)',
        'mr': 'मराठी (Marathi)',
        'gu': 'ગુજરાતી (Gujarati)',
        'kn': 'ಕನ್ನಡ (Kannada)',
        'ml': 'മലയാളം (Malayalam)',
        'pa': 'ਪੰਜਾਬੀ (Punjabi)'
    }
    
    # Image Processing
    IMG_SIZE = (256, 256)
    
    @staticmethod
    def init_app(app):
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.MODEL_PATH, exist_ok=True)