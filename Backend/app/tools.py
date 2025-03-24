from langchain_core.tools import tool
from gtts import gTTS
from language_tool_python import LanguageTool
from deep_translator import GoogleTranslator
import os

@tool
def check_grammar(text: str) -> str:
    """Checks the grammar of the input text in German and returns corrections or confirmation."""
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
    """Defines a German word using a mock dictionary."""
    try:
        if not word.strip():
            return "Please provide a word to define."
        mock_definitions = {"Haus": "house", "Auto": "car", "lernen": "to learn"}
        return mock_definitions.get(word.lower(), f"No definition found for '{word}'. Try another word!")
    except Exception as e:
        return f"Error defining word: {str(e)}"

@tool
def pronounce_text(text: str) -> str:
    """Generates pronunciation audio for the given text in German and returns the file URL."""
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
    """Translates the given text to English."""
    try:
        if not text.strip():
            return "Please provide text to translate to English."
        translator = GoogleTranslator(source='auto', target='en')
        result = translator.translate(text)
        print(f"Translated (to English): {result}")
        return result
    except Exception as e:
        return f"Error translating to English: {str(e)}"

@tool
def language_translator_bn(text: str) -> str:
    """Translates the given text to Bengali (Bangla)."""
    try:
        if not text.strip():
            return "Please provide text to translate to Bengali."
        translator = GoogleTranslator(source='auto', target='bn')
        result = translator.translate(text)
        print(f"Translated (to Bengali): {result}")
        return result
    except Exception as e:
        return f"Error translating to Bengali: {str(e)}"

@tool
def explain_grammar(text: str) -> str:
    """Explains the grammar of the given German text in German and English."""
    try:
        if not text.strip():
            return "Please provide text to explain grammar."

        tool = LanguageTool('de-DE')
        matches = tool.check(text)
        print("explain_grammar")
        # Basic grammar analysis (expand as needed)
        explanation_de = "Grammatikalische Erklärung:\n"
        explanation_en = "Grammar Explanation:\n"
        
        if not matches:
            explanation_de += "Der Satz ist grammatikalisch korrekt.\n"
            explanation_en += "The sentence is grammatically correct.\n"
        else:
            for match in matches:
                explanation_de += f"- {match.ruleId}: {match.message} (z.B. {match.context})\n"
                explanation_en += f"- {match.ruleId}: {GoogleTranslator(source='auto', target='en').translate(match.message)} (e.g., {match.context})\n"

        # Add simple structure explanation (example)
        words = text.split()
        if len(words) >= 3 and "bin" in words:
            explanation_de += "Struktur: Subjekt + Verb + Adjektiv (z.B. 'Ich bin gut').\n"
            explanation_en += "Structure: Subject + Verb + Adjective (e.g., 'I am good').\n"

        return f"{explanation_de}\n{explanation_en}"
    except Exception as e:
        return f"Error explaining grammar: {str(e)}"