from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime

from config import Config
from database import Database
from agents.vision_agent import VisionAgent
from agents.decision_agent import DecisionAgent
from agents.garden_agent import GardenKnowledgeAgent
from agents.weather_agent import WeatherAgent
from utils.location import LocationAgent 

app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)

# Initialize agents
db = Database()
vision_agent = VisionAgent()
location_agent = LocationAgent()
decision_agent = DecisionAgent()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Home page"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    return render_template('index.html', languages=Config.LANGUAGES, crops=Config.CROPS)

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze uploaded plant image"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        crop_type = request.form.get('crop_type', 'auto')
        language = request.form.get('language', 'en')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Use JPG, JPEG, or PNG'}), 400
        
        # Save uploaded file
        filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Get location
        user_ip = request.remote_addr
        location = location_agent.get_location_from_ip(user_ip)
        
        # Get weather
        weather = location_agent.get_weather(location['lat'], location['lon'])
        
        # Detect disease
        if crop_type == 'auto':
            detection = vision_agent.auto_detect_crop(filepath)
        else:
            detection = vision_agent.detect_disease(filepath, crop_type)
        
        if 'error' in detection and detection['confidence'] == 0:
            return jsonify({'error': detection['error']}), 400
        
        # Generate recommendations
        recommendations = decision_agent.generate_recommendations(
            detection, weather, location, language
        )
        
        # Save to database
        detection_id = db.save_detection(
            session['user_id'],
            filepath,
            detection['crop'],
            detection['disease'],
            detection['confidence'],
            location,
            language
        )
        
        db.save_recommendation(detection_id, recommendations, weather)
        
        return jsonify({
            'detection_id': str(detection_id),
            'detection': detection,
            'location': location,
            'weather': weather,
            'recommendations': recommendations,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        print(f"Error in analyze: {e}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/history')
def history():
    """User's analysis history"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('index'))
    
    history = db.get_user_history(user_id)
    stats = db.get_statistics(user_id)
    
    return render_template('history.html', history=history, stats=stats)

@app.route('/detection/<detection_id>')
def view_detection(detection_id):
    """View specific detection details"""
    detection = db.get_detection_by_id(detection_id)
    if not detection:
        return "Detection not found", 404
    
    recommendations = db.get_recommendations(detection_id)
    return render_template('detection.html', detection=detection, recommendations=recommendations)

@app.route('/translate', methods=['POST'])
def translate():
    """Translate text to selected language"""
    data = request.get_json()
    text = data.get('text')
    language = data.get('language', 'en')
    
    if language == 'en':
        return jsonify({'translated': text})
    
    translated = decision_agent.translate_text(text, language)
    return jsonify({'translated': translated})

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'models_loaded': len(vision_agent.models),
        'supported_crops': Config.CROPS,
        'supported_languages': list(Config.LANGUAGES.keys())
    })

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/guide')
def guide():
    """User guide page"""
    return render_template('guide.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)