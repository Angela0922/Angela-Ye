from googletrans import Translator

translator = Translator()

def translate_text(text: str) -> str:
    result = translator.translate(text, src='es', dest='en')
    return result.text