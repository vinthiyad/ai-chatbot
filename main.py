from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# load API key from .env file
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# conversation history stored here
history = []

# system instruction for this business
SYSTEM_PROMPT = """You are a helpful assistant for G-TAX Consultancy Chennai.
You help clients with GST, Income Tax, and Company Registration queries.
Always be polite and professional.
If you don't know something, say 'Please call us at +91 98402 38206'
Keep answers short and clear."""

app = FastAPI()

# allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# define what user sends
class Message(BaseModel):
    text: str

# the chat endpoint
@app.post("/chat")
async def chat_endpoint(message: Message):
    # add user message to history
    history.append(
        types.Content(role="user", parts=[types.Part(text=message.text)])
    )

    # send to Gemini with full history
    response = client.models.generate_content(
   model="gemini-2.5-flash",
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
        contents=history
    )

    reply = response.text

    # add AI reply to history
    history.append(
        types.Content(role="model", parts=[types.Part(text=reply)])
    )

    return {"reply": reply}

# health check
@app.get("/")
async def root():
    return {"status": "AI Chatbot is running"}


@app.get("/app")
async def serve_chat():
    return FileResponse("index.html")