from fastapi import APIRouter, HTTPException
from app.models import ChatRequest
from app.database import save_message, get_chat_history, clear_chat_history
from app.agents import app_graph

router = APIRouter()

@router.post("/chat")
async def process_chat(request: ChatRequest):
    user_id = request.user_id
    message = request.message
    
    save_message(user_id, f"You: {message}")
    
    state = {"messages": [{"role": "human", "content": message}], "next": ""}
    final_state = None
    for output in app_graph.stream(state):
        final_state = output
    
    if not final_state:
        raise HTTPException(status_code=500, detail="Failed to process message")
    
    for key, value in final_state.items():
        if "messages" in value and value["messages"]:
            response = value["messages"][-1]["content"]
            save_message(user_id, f"Teacher: {response}")
            return {"response": response, "timestamp": get_chat_history(user_id)[-1]["timestamp"]}
    
    raise HTTPException(status_code=500, detail="No response generated")

@router.get("/history/{user_id}")
async def get_history(user_id: str):
    history = get_chat_history(user_id)
    return {"history": history}

@router.delete("/history/{user_id}")
async def clear_history(user_id: str):
    clear_chat_history(user_id)
    return {"message": "Chat history cleared"}