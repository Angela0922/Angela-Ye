import openai
import whisper
import os
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()

class TranslationService:
    def __init__(self):
        # Initialize OpenAI API
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        # Load Whisper model for speech recognition
        self.whisper_model = whisper.load_model("base")
        
        self.temp_dir = "temp"
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def transcribe_audio(self, audio_path):
        """Transcribe Spanish audio to text using Whisper"""
        try:
            result = self.whisper_model.transcribe(audio_path, language='es')
            return result["text"].strip()
        except Exception as e:
            raise Exception(f"Error transcribing audio: {str(e)}")
    
    def translate_text(self, spanish_text):
        """Translate Spanish text to English using OpenAI"""
        try:
            if not openai.api_key:
                # Fallback: Simple translation simulation for demo
                return f"[ENGLISH TRANSLATION] {spanish_text}"
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional translator. Translate the following Spanish text to natural, fluent English. Maintain the tone and style appropriate for TikTok e-commerce content. Only return the translated text, no explanations."
                    },
                    {
                        "role": "user",
                        "content": spanish_text
                    }
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            # Fallback for demo purposes
            print(f"OpenAI translation failed: {str(e)}")
            return f"[ENGLISH TRANSLATION] {spanish_text}"
    
    def text_to_speech(self, english_text, job_id):
        """Convert English text to speech using gTTS"""
        try:
            # Use gTTS for text-to-speech
            tts = gTTS(text=english_text, lang='en', slow=False)
            
            output_path = os.path.join(self.temp_dir, f"english_audio_{job_id}.mp3")
            tts.save(output_path)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Error generating speech: {str(e)}")
    
    def enhance_translation_for_ecommerce(self, text):
        """Enhance translation specifically for e-commerce content"""
        try:
            if not openai.api_key:
                return text
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert in e-commerce marketing translation. 
                        Enhance this translated text to be more engaging for American TikTok e-commerce audiences. 
                        Make it sound natural, trendy, and compelling for online shopping. 
                        Keep the same length and meaning but optimize for American social media culture."""
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Enhancement failed: {str(e)}")
            return text
    
    def get_audio_duration(self, audio_path):
        """Get duration of audio file"""
        try:
            import librosa
            y, sr = librosa.load(audio_path)
            duration = librosa.get_duration(y=y, sr=sr)
            return duration
        except:
            # Fallback method
            try:
                from moviepy.editor import AudioFileClip
                audio = AudioFileClip(audio_path)
                duration = audio.duration
                audio.close()
                return duration
            except:
                return None