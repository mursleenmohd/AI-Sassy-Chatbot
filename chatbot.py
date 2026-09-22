import os
import json
import tiktoken
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from google import genai
from google.genai import types
from dotenv import load_dotenv

from database import init_db, get_db, ChatHistory

load_dotenv(override=True)

app = FastAPI(title="AI API Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable is not set in .env file.")

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL = "gemini-3.6-flash"
SYSTEM_PROMPT = "You are a fed up and sassy assistant who hates answering questions."

class ChatRequest(BaseModel):
    session_id: str
    user_input: str

def count_tokens(text: str) -> int:
    try:
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

@app.post("/chat/stream")
async def stream_chat(request: ChatRequest, db: Session = Depends(get_db)):
    history = db.query(ChatHistory).filter(ChatHistory.session_id == request.session_id).all()
    
    contents = []
    for msg in history:
        if msg.user_message and msg.user_message.strip():
            contents.append(types.Content(role="user", parts=[types.Part.from_text(text=msg.user_message)]))
        if msg.bot_response and msg.bot_response.strip():
            contents.append(types.Content(role="model", parts=[types.Part.from_text(text=msg.bot_response)]))
    
    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=request.user_input)]))

    def event_generator():
        full_response = ""
        try:
            config = types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7,
                max_output_tokens=1024  # Increased token limit so text never gets cut off
            )

            response_stream = client.models.generate_content_stream(
                model=MODEL,
                contents=contents,
                config=config
            )

            for chunk in response_stream:
                if chunk.text:
                    full_response += chunk.text
                    payload = json.dumps({"content": chunk.text})
                    yield f"data: {payload}\n\n"

        except Exception as e:
            print(f"Backend Streaming Error: {e}")
            error_payload = json.dumps({"content": f"\n[Error: {str(e)}]"})
            yield f"data: {error_payload}\n\n"

        if full_response.strip():
            tokens = count_tokens(full_response)
            db_chat = ChatHistory(
                session_id=request.session_id,
                user_message=request.user_input,
                bot_response=full_response,
                tokens_used=tokens
            )
            db.add(db_chat)
            db.commit()

    return StreamingResponse(event_generator(), media_type="text/event-stream")