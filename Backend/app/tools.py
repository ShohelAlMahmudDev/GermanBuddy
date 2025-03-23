from langchain_core.tools import tool
from gtts import gTTS
from language_tool_python import LanguageTool

@tool
def check_grammar(text: str) -> str:
    """Checks the grammar of the input text and returns corrections."""
    tool = LanguageTool('de-DE')
    matches = tool.check(text)
    if not matches:
        return "No grammar errors found!"
    corrections = [f"Error: {match.ruleId} - {match.message}" for match in matches]
    return "\n".join(corrections)

@tool
def define_word(word: str) -> str:
    """Defines a German word using a mock dictionary."""
    mock_definitions = {"Haus": "house", "Auto": "car", "lernen": "to learn"}
    return mock_definitions.get(word, f"No definition found for '{word}'. Try another word!")

@tool
def pronounce_text(text: str) -> str:
    """Generates pronunciation audio for the given text and returns the file URL."""
    audio_file = "static/pronunciation.mp3"
    tts = gTTS(text=text, lang='de')
    tts.save(audio_file)
    return "/static/pronunciation.mp3"