import speech_recognition as sr
from gtts import gTTS
from googletrans import Translator
import io
import logging

logger = logging.getLogger(__name__)

class TranslationHelper:
    def __init__(self):
        self.translator = Translator()
        self.recognizer = sr.Recognizer()
        
        # Language codes mapping for speech recognition
        self.lang_codes = {
            'en': 'en-IN',
            'hi': 'hi-IN',
            'mr': 'mr-IN',
            'ta': 'ta-IN',
            'te': 'te-IN',
            'bn': 'bn-IN',
            'gu': 'gu-IN',
            'kn': 'kn-IN',
            'ml': 'ml-IN',
            'pa': 'pa-IN'
        }
    
    def speech_to_text(self, audio_file_path, language='en'):
        """
        Convert speech to text
        """
        try:
            with sr.AudioFile(audio_file_path) as source:
                audio = self.recognizer.record(source)
            
            # Get language code
            lang_code = self.lang_codes.get(language, 'en-IN')
            
            # Recognize speech
            text = self.recognizer.recognize_google(audio, language=lang_code)
            logger.info(f"Speech recognized: {text}")
            return text
            
        except sr.UnknownValueError:
            logger.warning("Speech not understood")
            return "Sorry, I couldn't understand the audio."
        except sr.RequestError as e:
            logger.error(f"Speech recognition error: {str(e)}")
            return "Speech recognition service error."
        except Exception as e:
            logger.error(f"Speech to text failed: {str(e)}")
            raise
    
    def text_to_speech(self, text, language='en'):
        """
        Convert text to speech
        Returns audio data as bytes
        """
        try:
            # Create TTS object
            tts = gTTS(text=text, lang=language, slow=False)
            
            # Save to bytes buffer
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            return audio_buffer.read()
            
        except Exception as e:
            logger.error(f"Text to speech failed: {str(e)}")
            raise
    
    def translate(self, text, source='auto', target='en'):
        """
        Translate text between languages
        """
        try:
            translation = self.translator.translate(text, src=source, dest=target)
            return translation.text
        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            return text  # Return original text if translation fails
    
    def detect_language(self, text):
        """
        Detect language of text
        """
        try:
            detection = self.translator.detect(text)
            return detection.lang
        except Exception as e:
            logger.error(f"Language detection failed: {str(e)}")
            return 'en'