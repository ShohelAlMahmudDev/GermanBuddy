from langchain_core.tools import tool
from gtts import gTTS
from language_tool_python import LanguageTool
from deep_translator import GoogleTranslator
import os

@tool
def check_grammar(text: str) -> str:
    """Checks the grammar of the input text in German and returns corrections or confirmation.
    
    Args:
        text (str): The text to check for grammatical errors
        
    Returns:
        str: A message indicating no errors or listing corrections
    """
    try:
        if not text.strip():
            return "Please provide text to check grammar."
        tool = LanguageTool('de-DE')
        matches = tool.check(text)
        if not matches:
            return "No grammar errors found!"
        corrections = [f"Error: {match.ruleId} - {match.message}" for match in matches]
        return "\n".join(corrections)
    except Exception as e:
        return f"Error checking grammar: {str(e)}"

@tool
def define_word(word: str) -> str:
    """Defines a German word using a mock dictionary.
    
    Args:
        word (str): The German word to define
        
    Returns:
        str: The definition if found, or an error message if not
    """
    try:
        if not word.strip():
            return "Please provide a word to define."
        mock_definitions = {"Haus": "house", "Auto": "car", "lernen": "to learn"}
        return mock_definitions.get(word.lower(), f"No definition found for '{word}'. Try another word!")
    except Exception as e:
        return f"Error defining word: {str(e)}"

@tool
def pronounce_text(text: str) -> str:
    """Generates pronunciation audio for the given text in German and returns the file URL.
    
    Args:
        text (str): The text to pronounce
        
    Returns:
        str: The URL to the generated audio file
    """
    try:
        if not text.strip():
            return "Please provide text to pronounce."
        os.makedirs("static", exist_ok=True)
        audio_file = "static/pronunciation.mp3"
        tts = gTTS(text=text, lang='de')
        tts.save(audio_file)
        return "/static/pronunciation.mp3"
    except Exception as e:
        return f"Error generating pronunciation: {str(e)}"

@tool
def language_translator_en(text: str) -> str:
    """Translates the given text to English.
    
    Args:
        text (str): The text to translate to English
        
    Returns:
        str: The translated text in English
    """
    try:
        if not text.strip():
            return "Please provide text to translate to English."
        translator = GoogleTranslator(source='auto', target='en')
        result = translator.translate(text)
        #print(f"Translated (to English): {result}")
        return result
    except Exception as e:
        return f"Error translating to English: {str(e)}"

@tool
def language_translator_bn(text: str) -> str:
    """Translates the given text to Bengali (Bangla).
    
    Args:
        text (str): The text to translate to Bengali
        
    Returns:
        str: The translated text in Bengali
    """
    try:
        if not text.strip():
            return "Please provide text to translate to Bengali."
        translator = GoogleTranslator(source='auto', target='bn')
        result = translator.translate(text)
        #print(f"Translated (to Bengali): {result}")
        # Verify Bangla output (optional debugging)
        if result == text and translator.detect(text) != 'bn':
            return "Translation failed: No Bangla output generated."
        return result
    except Exception as e:
        return f"Error translating to Bengali: {str(e)}"