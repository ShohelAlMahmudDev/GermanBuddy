import os
import sqlite3
from typing import List, Dict
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware  # Add this import
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from gtts import gTTS
from language_tool_python import LanguageTool
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="langchain")

# Load environment variables
load_dotenv()
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
if not deepseek_api_key:
    raise ValueError("Please set the DEEPSEEK_API_KEY environment variable in .env")

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, DELETE, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Mount static files for serving audio
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize DeepSeek LLM with updated class
model = ChatOpenAI(
    model="deepseek-chat",
    api_key=deepseek_api_key,
    base_url="https://api.deepseek.com/v1",
    temperature=0.7
)

# Database setup
def init_db():
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history 
                 (user_id TEXT, timestamp TEXT, message TEXT)''')
    conn.commit()
    conn.close()

def save_message(user_id: str, message: str):
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute("INSERT INTO chat_history (user_id, timestamp, message) VALUES (?, datetime('now'), ?)", 
              (user_id, message))
    conn.commit()
    conn.close()

def get_chat_history(user_id: str) -> List[dict]:
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute("SELECT timestamp, message FROM chat_history WHERE user_id = ? ORDER BY timestamp", (user_id,))
    history = [{"timestamp": row[0], "message": row[1]} for row in c.fetchall()]
    conn.close()
    return history

# Tools with added docstrings
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

# Custom State Type
State = Dict[str, List[dict]]

# Agent Functions
progress = UserProgress()

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
    response = model.invoke([HumanMessage(content=prompt)]).content
    state["messages"].append({"role": "ai", "content": response})
    state["next"] = END
    return state

# Define the Graph
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

app_graph = graph.compile()

# Pydantic model for request
class ChatRequest(BaseModel):
    user_id: str
    message: str

# API Endpoints
@app.post("/chat")
async def process_chat(request: ChatRequest):
    user_id = request.user_id
    message = request.message
    
    # Save user message
    save_message(user_id, f"You: {message}")
    
    # Process with agent graph
    state = {"messages": [{"role": "human", "content": message}], "next": ""}
    final_state = None
    for output in app_graph.stream(state):
        final_state = output
    
    if not final_state:
        raise HTTPException(status_code=500, detail="Failed to process message")
    
    # Extract and save response
    for key, value in final_state.items():
        if "messages" in value and value["messages"]:
            response = value["messages"][-1]["content"]
            save_message(user_id, f"Teacher: {response}")
            conn = sqlite3.connect("chat_history.db")
            c = conn.cursor()
            c.execute("SELECT timestamp FROM chat_history WHERE user_id = ? AND message = ? ORDER BY timestamp DESC LIMIT 1", 
                      (user_id, f"Teacher: {response}"))
            timestamp = c.fetchone()[0]
            conn.close()
            return {"response": response, "timestamp": timestamp}
    
    raise HTTPException(status_code=500, detail="No response generated")

@app.get("/history/{user_id}")
async def get_history(user_id: str):
    history = get_chat_history(user_id)
    return {"history": history}

@app.delete("/history/{user_id}")
async def clear_history(user_id: str):
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return {"message": "Chat history cleared"}

# Initialize DB on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    if not os.path.exists("static"):
        os.makedirs("static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)