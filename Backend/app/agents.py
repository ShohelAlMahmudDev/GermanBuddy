from typing import List, Dict
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from app.config import get_llm
from app.tools import check_grammar, define_word, pronounce_text
from googletrans import Translator
# Custom State Type
State = Dict[str, List[dict]]

# Adaptive Difficulty Logic
class UserProgress:
    def __init__(self):
        self.correct_answers = 0
        self.total_questions = 0
    
    def update(self, is_correct: bool):
        self.total_questions += 1
        if is_correct:
            self.correct_answers += 1
    
    def get_level(self) -> str:
        accuracy = self.correct_answers / self.total_questions if self.total_questions > 0 else 0
        if accuracy > 0.8:
            return "advanced"
        elif accuracy > 0.5:
            return "intermediate"
        return "beginner"

progress = UserProgress()

# Agent Functions
def teacher_agent(state: State) -> State:
    user_input = state["messages"][-1]["content"].lower()
    if "grammar" in user_input:
        state["next"] = "grammar_agent"
    elif "vocabulary" in user_input or "word" in user_input:
        state["next"] = "vocabulary_agent"
    elif "pronounce" in user_input or "pronunciation" in user_input:
        state["next"] = "pronunciation_agent"
    else:
        state["next"] = "conversation_agent"
    return state

def grammar_agent(state: State) -> State:
    user_input = state["messages"][-1]["content"]
    response = check_grammar(user_input)
    state["messages"].append({"role": "ai", "content": response})
    progress.update("No grammar errors" in response)
    state["next"] = END
    return state

def vocabulary_agent(state: State) -> State:
    user_input = state["messages"][-1]["content"]
    word = user_input.split()[-1]
    response = define_word(word)
    state["messages"].append({"role": "ai", "content": response})
    state["next"] = END
    return state

def pronunciation_agent(state: State) -> State:
    user_input = state["messages"][-1]["content"]
    audio_file = pronounce_text(user_input)
    response = f"Pronunciation audio generated: {audio_file}"
    state["messages"].append({"role": "ai", "content": response})
    state["next"] = END
    return state

def conversation_agent(state: State) -> State:
    user_input = state["messages"][-1]["content"]
    level = progress.get_level()
    prompt = f"Respond in German at {level} level to: {user_input}"
    response = get_llm().invoke([HumanMessage(content=prompt)]).content
    state["messages"].append({"role": "ai", "content": response})
    state["next"] = END
    return state

def language_translator(question:str):
  # Initialize the translator
  translator = Translator()

  # Translate from English to Bengali
  result = translator.translate(question, dest='en')
  print("Translated (English ➜ Bengali):", result.text)
  result = translator.translate(question, dest='bn')
  # Translate from German to Bengali
  #result = translator.translate("Hallo, wie geht es dir?", src='de', dest='bn')
  print("Translated (German ➜ Bengali):", result.text)
# Define and compile the graph
def create_graph():
    graph = StateGraph(State)
    graph.add_node("teacher_agent", teacher_agent)
    graph.add_node("grammar_agent", grammar_agent)
    graph.add_node("vocabulary_agent", vocabulary_agent)
    graph.add_node("pronunciation_agent", pronunciation_agent)
    graph.add_node("conversation_agent", conversation_agent)

    graph.set_entry_point("teacher_agent")
    graph.add_conditional_edges(
        "teacher_agent",
        lambda state: state["next"],
        {
            "grammar_agent": "grammar_agent",
            "vocabulary_agent": "vocabulary_agent",
            "pronunciation_agent": "pronunciation_agent",
            "conversation_agent": "conversation_agent",
            END: END
        }
    )
    return graph.compile()

app_graph = create_graph()