from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent import ai_agent
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Estecharat AI Assistant", version="1.0")

# Setup CORS for local testing/frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str

@app.post("/api/ai/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not request.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
        
    try:
        # Invoke the LangChain agent with the memory session context
        response = ai_agent.invoke(
            {
                "input": request.message,
                "session_id": request.session_id
            },
            config={"configurable": {"session_id": request.session_id}}
        )
        return ChatResponse(reply=response["output"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"status": "AI Agent is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
