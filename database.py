from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
from config import Config

class Database:
    def __init__(self):
        self.client = MongoClient(Config.MONGODB_URI)
        self.db = self.client[Config.DATABASE_NAME]
        self.detections = self.db.detections
        self.users = self.db.users
        self.recommendations = self.db.recommendations
        
    def save_detection(self, user_id, image_path, crop_type, disease, confidence, location, language='en'):
        """Save disease detection result"""
        detection = {
            'user_id': user_id,
            'image_path': image_path,
            'crop_type': crop_type,
            'disease': disease,
            'confidence': float(confidence),
            'location': location,
            'language': language,
            'timestamp': datetime.utcnow(),
            'status': 'active'
        }
        return self.detections.insert_one(detection).inserted_id
    
    def save_recommendation(self, detection_id, recommendations, weather_data):
        """Save AI-generated recommendations"""
        rec = {
            'detection_id': detection_id,
            'recommendations': recommendations,
            'weather_data': weather_data,
            'timestamp': datetime.utcnow()
        }
        return self.recommendations.insert_one(rec).inserted_id
    
    def get_user_history(self, user_id, limit=10):
        """Get user's detection history"""
        return list(self.detections.find(
            {'user_id': user_id}
        ).sort('timestamp', -1).limit(limit))
    
    def get_detection_by_id(self, detection_id):
        """Get specific detection"""
        return self.detections.find_one({'_id': ObjectId(detection_id)})
    
    def get_recommendations(self, detection_id):
        """Get recommendations for a detection"""
        return self.recommendations.find_one({'detection_id': detection_id})
    
    def update_detection_status(self, detection_id, status):
        """Update detection status"""
        return self.detections.update_one(
            {'_id': ObjectId(detection_id)},
            {'$set': {'status': status, 'updated_at': datetime.utcnow()}}
        )
    
    def get_statistics(self, user_id=None):
        """Get usage statistics"""
        query = {'user_id': user_id} if user_id else {}
        total = self.detections.count_documents(query)
        by_crop = list(self.detections.aggregate([
            {'$match': query},
            {'$group': {'_id': '$crop_type', 'count': {'$sum': 1}}}
        ]))
        return {
            'total_detections': total,
            'by_crop': {item['_id']: item['count'] for item in by_crop}
        }