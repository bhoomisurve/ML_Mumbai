import tensorflow as tf
import numpy as np
from PIL import Image
import os
from config import Config

class VisionAgent:
    def __init__(self):
        self.models = {}
        self.class_names = {
            'apple': ['Apple_scab', 'Black_rot', 'Cedar_apple_rust', 'Healthy'],
            'cherry': ['Powdery_mildew', 'Healthy'],
            'corn': ['Cercospora_leaf_spot', 'Common_rust', 'Northern_Leaf_Blight', 'Healthy'],
            'grape': ['Black_rot', 'Esca', 'Leaf_blight', 'Healthy'],
            'peach': ['Bacterial_spot', 'Healthy'],
            'pepper': ['Bacterial_spot', 'Healthy'],
            'potato': ['Early_blight', 'Late_blight', 'Healthy'],
            'strawberry': ['Leaf_scorch', 'Healthy'],
            'tomato': ['Bacterial_spot', 'Early_blight', 'Late_blight', 'Leaf_Mold', 
                       'Septoria_leaf_spot', 'Spider_mites', 'Target_Spot', 
                       'Tomato_Yellow_Leaf_Curl_Virus', 'Tomato_mosaic_virus', 'Healthy']
        }
        self.load_models()
    
    def load_models(self):
        """Load all crop models"""
        for crop in Config.CROPS:
            model_path = os.path.join(Config.MODEL_PATH, f'{crop}_model.h5')
            if os.path.exists(model_path):
                try:
                    self.models[crop] = tf.keras.models.load_model(model_path)
                    print(f"Loaded {crop} model successfully")
                except Exception as e:
                    print(f"Error loading {crop} model: {e}")
    
    def preprocess_image(self, image_path):
        """Preprocess image for model input"""
        img = Image.open(image_path).convert('RGB')
        img = img.resize(Config.IMG_SIZE)
        img_array = np.array(img) / 255.0  # Normalize to [0, 1]
        img_array = np.expand_dims(img_array, axis=0)
        return img_array
    
    def detect_disease(self, image_path, crop_type):
        """Detect disease in crop image"""
        if crop_type not in self.models:
            return {
                'error': f'Model not available for {crop_type}',
                'crop': crop_type,
                'disease': 'Unknown',
                'confidence': 0.0,
                'all_predictions': {}
            }
        
        try:
            img_array = self.preprocess_image(image_path)
            predictions = self.models[crop_type].predict(img_array, verbose=0)
            predicted_class = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_class])
            
            disease = self.class_names[crop_type][predicted_class]
            
            # Get all predictions
            all_preds = {
                self.class_names[crop_type][i]: float(predictions[0][i])
                for i in range(len(predictions[0]))
            }
            
            return {
                'crop': crop_type,
                'disease': disease,
                'confidence': confidence,
                'all_predictions': all_preds,
                'is_healthy': 'Healthy' in disease
            }
        except Exception as e:
            return {
                'error': str(e),
                'crop': crop_type,
                'disease': 'Error',
                'confidence': 0.0,
                'all_predictions': {}
            }
    
    def auto_detect_crop(self, image_path):
        """Try to detect which crop type from image (run all models)"""
        best_result = None
        best_confidence = 0.0
        
        for crop in self.models.keys():
            result = self.detect_disease(image_path, crop)
            if result.get('confidence', 0) > best_confidence:
                best_confidence = result['confidence']
                best_result = result
        
        return best_result if best_result else {
            'error': 'Could not detect crop type',
            'crop': 'unknown',
            'disease': 'Unknown',
            'confidence': 0.0
        }