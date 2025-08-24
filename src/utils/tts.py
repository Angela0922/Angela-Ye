from gtts import gTTS

def text_to_speech(text: str, output_wav: str):
    tts = gTTS(text, lang='en')
    tts.save(output_wav)