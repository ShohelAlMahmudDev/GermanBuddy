from typing import List, Dict, TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from app.config import get_llm
from app.tools import check_grammar, define_word, pronounce_text, language_translator_en, language_translator_bn, explain_grammar
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StateType(TypedDict):
    messages: List[Dict[str, str]]
    next: str

State = StateType

class UserProgress:
    def __init__(self):
        self.correct_answers = 0
        self.total_questions = 0
        self.level_thresholds = {"advanced": 0.8, "intermediate": 0.5}
    
    def update(self, is_correct: bool) -> None:
        """Update progress based on user performance"""
        self.total_questions += 1
        if is_correct:
            self.correct_answers += 1
        logger.info(f"Progress updated: {self.correct_answers}/{self.total_questions}")
    
    def get_level(self) -> str:
        """Determine user level based on accuracy"""
        accuracy = self.correct_answers / self.total_questions if self.total_questions > 0 else 0
        if accuracy > self.level_thresholds["advanced"]:
            return "advanced"
        elif accuracy > self.level_thresholds["intermediate"]:
            return "intermediate"
        return "beginner"

progress = UserProgress()

def teacher_agent(state: State) -> State:
    """Route user input to the appropriate agent based on intent."""
    if not state["messages"]:
        state["next"] = "conversation_agent"
        return state
        
    user_input = state["messages"][-1]["content"].lower().strip()
    logger.info(f"User input: {user_input}")
    if not user_input:
        state["next"] = "conversation_agent"
        return state

    intents = {
        "grammar_agent": ["grammar", "check grammar", "grammar check"],
        "vocabulary_agent": ["vocabulary", "word", "define", "meaning"],
        "pronunciation_agent": ["pronounce", "pronunciation", "say"],
        "translator_en_agent": ["translate to english", "translation english", "english", "en"],
        "translator_bn_agent": ["translate to bangla", "translation bangla", "bangla", "bn"],
        "grammar_explain_agent": ["explain grammar", "grammar explanation", "explain"],
    }
    
    state["next"] = "conversation_agent"  # Default to conversation
    for agent, keywords in intents.items():
        if any(keyword in user_input for keyword in keywords):
            state["next"] = agent
            logger.info(f"Routed to: {state['next']}")
            break
    return state

def grammar_agent(state: State) -> State:
    """Check grammar of user input."""
    try:
        user_input = state["messages"][-1]["content"]
        response = check_grammar.invoke(user_input)
        state["messages"].append({"role": "ai", "content": response})
        progress.update("No grammar errors" in response)
    except Exception as e:
        state["messages"].append({"role": "ai", "content": f"Error in grammar agent: {str(e)}"})
    state["next"] = END
    return state

def vocabulary_agent(state: State) -> State:
    """Define a word from user input."""
    try:
        user_input = state["messages"][-1]["content"].strip()
        words = user_input.split()
        response = define_word.invoke(words[-1] if words else "")
        state["messages"].append({"role": "ai", "content": response})
    except Exception as e:
        state["messages"].append({"role": "ai", "content": f"Error in vocabulary agent: {str(e)}"})
    state["next"] = END
    return state

def pronunciation_agent(state: State) -> State:
    """Generate pronunciation audio for text."""
    try:
        user_input = state["messages"][-1]["content"]
        response = pronounce_text.invoke(user_input)
        state["messages"].append({"role": "ai", "content": response})
    except Exception as e:
        state["messages"].append({"role": "ai", "content": f"Error in pronunciation agent: {str(e)}"})
    state["next"] = END
    return state

def translator_en_agent(state: State) -> State:
    """Translate user input to English."""
    try:
        user_input = state["messages"][-1]["content"]
        if "translate to english" in user_input.lower():
            text_to_translate = user_input.lower().split("translate to english")[-1].strip()
        else:
            text_to_translate = user_input
        response = language_translator_en.invoke(text_to_translate)
        full_response = f"English: {response}"
        logger.info(f"English translation: {full_response}")
        state["messages"].append({"role": "ai", "content": full_response})
    except Exception as e:
        state["messages"].append({"role": "ai", "content": f"Error in English translation: {str(e)}"})
    state["next"] = END
    return state

def translator_bn_agent(state: State) -> State:
    """Translate user input to Bengali."""
    try:
        user_input = state["messages"][-1]["content"]
        if "translate to bangla" in user_input.lower():
            text_to_translate = user_input.lower().split("translate to bangla")[-1].strip()
        else:
            text_to_translate = user_input
        response = language_translator_bn.invoke(text_to_translate)
        full_response = f"Bangla: {response}"
        logger.info(f"Bangla translation: {full_response}")
        state["messages"].append({"role": "ai", "content": full_response})
    except Exception as e:
        state["messages"].append({"role": "ai", "content": f"Error in Bangla translation: {str(e)}"})
    state["next"] = END
    return state

def grammar_explain_agent(state: State) -> State:
    """Explain the grammar of the user input in German and English."""
    try:
        user_input = state["messages"][-1]["content"]
        if "explain grammar" in user_input.lower():
            text_to_explain = user_input.lower().split("explain grammar")[-1].strip()
        else:
            text_to_explain = user_input
        response = explain_grammar.invoke(text_to_explain)
        state["messages"].append({"role": "ai", "content": response})
    except Exception as e:
        state["messages"].append({"role": "ai", "content": f"Error in grammar explanation: {str(e)}"})
    state["next"] = END
    return state

def conversation_agent(state: State) -> State:
    """Handle general conversation in German with English and Bangla translations."""
    try:
        user_input = state["messages"][-1]["content"]
        level = progress.get_level()
        prompt = f"Respond in German at {level} level to: {user_input}"
        german_response = get_llm().invoke([HumanMessage(content=prompt)]).content.strip()
        
        english_response = language_translator_en.invoke(german_response)
        bangla_response = language_translator_bn.invoke(german_response)
        
        full_response = (
            f"{german_response}\n"
            f"{english_response}\n"
            f"{bangla_response}"
        )
        logger.info(f"Full conversation response: {full_response}")
        state["messages"].append({"role": "ai", "content": full_response})
    except Exception as e:
        error_msg = f"Error in conversation: {str(e)}"
        logger.error(error_msg)
        state["messages"].append({"role": "ai", "content": error_msg})
    state["next"] = END
    return state

def create_graph() -> StateGraph:
    """Create and compile the state graph."""
    try:
        graph = StateGraph(State)
        graph.add_node("teacher_agent", teacher_agent)
        graph.add_node("grammar_agent", grammar_agent)
        graph.add_node("vocabulary_agent", vocabulary_agent)
        graph.add_node("pronunciation_agent", pronunciation_agent)
        graph.add_node("translator_en_agent", translator_en_agent)
        graph.add_node("translator_bn_agent", translator_bn_agent)
        graph.add_node("grammar_explain_agent", grammar_explain_agent)
        graph.add_node("conversation_agent", conversation_agent)

        graph.set_entry_point("teacher_agent")
        graph.add_conditional_edges(
            "teacher_agent",
            lambda state: state["next"],
            {
                "grammar_agent": "grammar_agent",
                "vocabulary_agent": "vocabulary_agent",
                "pronunciation_agent": "pronunciation_agent",
                "translator_en_agent": "translator_en_agent",
                "translator_bn_agent": "translator_bn_agent",
                "grammar_explain_agent": "grammar_explain_agent",
                "conversation_agent": "conversation_agent",
                END: END
            }
        )
        compiled_graph = graph.compile()
        logger.info("Graph successfully compiled")
        return compiled_graph
    except Exception as e:
        logger.error(f"Failed to create graph: {str(e)}")
        raise RuntimeError(f"Failed to create graph: {str(e)}")

app_graph = create_graph()