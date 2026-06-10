from fastapi import APIRouter
from pydantic import BaseModel
from app.services.openai_service import get_chat_response

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    message: str

@router.post("/")
async def chat(data: ChatRequest):
    messages = [
        {"role": "user", "content": data.message}
    ]
    reply = await get_chat_response(messages)
    return {"reply": reply}