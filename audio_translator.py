import os
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
from pydub import AudioSegment
from pydub.silence import split_on_silence
import numpy as np
from typing import Optional, Tuple
import logging
import tempfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioTranslator:
    """Handles audio extraction, speech recognition, translation, and text-to-speech synthesis."""
    
    def __init__(self):
        self.translator = Translator()
        self.recognizer = sr.Recognizer()
        self.temp_dir = "temp_audio"
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def extract_audio(self, video_path: str) -> str:
        """
        Extract audio from video file.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Path to extracted audio file
        """
        from moviepy.editor import VideoFileClip
        
        logger.info(f"Extracting audio from {video_path}")
        
        video = VideoFileClip(video_path)
        audio_path = os.path.join(self.temp_dir, "extracted_audio.wav")
        video.audio.write_audiofile(audio_path, verbose=False, logger=None)
        video.close()
        
        logger.info(f"Audio extracted to {audio_path}")
        return audio_path
    
    def transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribe audio to text using Google Speech Recognition.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Transcribed text
        """
        logger.info("Transcribing audio...")
        
        # Load audio file
        with sr.AudioFile(audio_path) as source:
            audio = self.recognizer.record(source)
        
        try:
            # Recognize speech (assuming Spanish)
            text = self.recognizer.recognize_google(audio, language='es-ES')
            logger.info(f"Transcribed text: {text}")
            return text
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return ""
        except sr.RequestError as e:
            logger.error(f"Could not request results: {e}")
            return ""
    
    def translate_text(self, text: str, source_lang: str = 'es', target_lang: str = 'en') -> str:
        """
        Translate text from source language to target language.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Translated text
        """
        if not text.strip():
            return ""
        
        logger.info(f"Translating from {source_lang} to {target_lang}")
        
        try:
            translation = self.translator.translate(text, src=source_lang, dest=target_lang)
            translated_text = translation.text
            logger.info(f"Translated text: {translated_text}")
            return translated_text
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text
    
    def synthesize_speech(self, text: str, output_path: str, lang: str = 'en') -> str:
        """
        Convert text to speech using Google Text-to-Speech.
        
        Args:
            text: Text to convert to speech
            output_path: Path for output audio file
            lang: Language code for speech synthesis
            
        Returns:
            Path to synthesized audio file
        """
        if not text.strip():
            # Create silent audio if no text
            silent_audio = AudioSegment.silent(duration=1000)  # 1 second silence
            silent_audio.export(output_path, format="wav")
            return output_path
        
        logger.info(f"Synthesizing speech for: {text[:50]}...")
        
        try:
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(output_path)
            logger.info(f"Speech synthesized to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Speech synthesis error: {e}")
            # Create silent audio as fallback
            silent_audio = AudioSegment.silent(duration=1000)
            silent_audio.export(output_path, format="wav")
            return output_path
    
    def process_audio(self, video_path: str, output_path: str) -> str:
        """
        Complete audio processing pipeline: extract, transcribe, translate, synthesize.
        
        Args:
            video_path: Path to input video
            output_path: Path for output audio
            
        Returns:
            Path to processed audio file
        """
        logger.info("Starting audio processing pipeline...")
        
        # Extract audio from video
        audio_path = self.extract_audio(video_path)
        
        # Transcribe audio
        transcribed_text = self.transcribe_audio(audio_path)
        
        if not transcribed_text:
            logger.warning("No speech detected, creating silent audio")
            silent_audio = AudioSegment.silent(duration=5000)  # 5 seconds silence
            silent_audio.export(output_path, format="wav")
            return output_path
        
        # Translate text
        translated_text = self.translate_text(transcribed_text)
        
        # Synthesize translated speech
        final_audio_path = self.synthesize_speech(translated_text, output_path)
        
        logger.info("Audio processing pipeline complete")
        return final_audio_path
    
    def adjust_audio_timing(self, audio_path: str, target_duration: float) -> str:
        """
        Adjust audio duration to match target duration.
        
        Args:
            audio_path: Path to audio file
            target_duration: Target duration in seconds
            
        Returns:
            Path to adjusted audio file
        """
        audio = AudioSegment.from_wav(audio_path)
        current_duration = len(audio) / 1000.0  # Convert to seconds
        
        if current_duration > target_duration:
            # Trim audio
            target_ms = int(target_duration * 1000)
            adjusted_audio = audio[:target_ms]
        elif current_duration < target_duration:
            # Extend audio with silence
            target_ms = int(target_duration * 1000)
            silence_needed = target_ms - len(audio)
            silence = AudioSegment.silent(duration=silence_needed)
            adjusted_audio = audio + silence
        else:
            adjusted_audio = audio
        
        adjusted_path = audio_path.replace('.wav', '_adjusted.wav')
        adjusted_audio.export(adjusted_path, format="wav")
        
        return adjusted_path
    
    def cleanup_temp_files(self):
        """Clean up temporary audio files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            logger.info("Cleaned up temporary audio files")