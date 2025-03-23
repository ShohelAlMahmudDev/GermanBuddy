import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.config import configure_cors, init_llm
from app.database import init_db
from app.routes import router

app = FastAPI()

# Configure CORS and mount static files
configure_cors(app)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize LLM and database
init_llm()
@app.on_event("startup")
async def startup_event():
    init_db()
    if not os.path.exists("static"):
        os.makedirs("static")

# Include API routes
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)