import os
import tempfile
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from agent import ai_agent
from fastapi.middleware.cors import CORSMiddleware
from config import OPENAI_API_KEY
from openai import OpenAI

app = FastAPI(title="Estecharat AI Assistant", version="1.0")
client = OpenAI(api_key=OPENAI_API_KEY)

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

class VoiceResponse(BaseModel):
    reply: str
    transcribed_text: str

@app.post("/api/ai/voice", response_model=VoiceResponse)
async def voice_endpoint(session_id: str = Form(...), audio: UploadFile = File(...)):
    try:
        # Save uploaded file temporarily
        suffix = ".webm"
        if audio.filename:
            _, ext = os.path.splitext(audio.filename)
            if ext:
                suffix = ext

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_audio:
            content = await audio.read()
            temp_audio.write(content)
            temp_audio_path = temp_audio.name

        # Transcribe using OpenAI Whisper
        with open(temp_audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file,
                prompt="مرحباً. دكتور، مستشفى، ألم، علاج. Hello. Doctor, hospital, pain, treatment."
            )
        
        # Delete temp file
        os.remove(temp_audio_path)

        transcribed_text = transcript.text
        if not transcribed_text:
             raise HTTPException(status_code=400, detail="Could not transcribe audio")

        # Invoke the LangChain agent with the memory session context
        response = ai_agent.invoke(
            {
                "input": transcribed_text,
                "session_id": session_id
            },
            config={"configurable": {"session_id": session_id}}
        )
        return VoiceResponse(reply=response["output"], transcribed_text=transcribed_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"status": "AI Agent is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
