from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import CurrentUser
from app.config import settings
from app.database import Chat, Message, get_db, utc_now
from app.polza import PolzaError, polza

router = APIRouter(prefix="api", tags=["chats"])
DbSession = Annotated[Session, Depends(get_db)]

class ChatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    created_at: datetime
    updated_at: datetime

class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    chat_id: int
    role: Literal["user", "assistant"]
    content: str
    model_id: str | None
    created_at: datetime

class ChatDetail(BaseModel):
    chat: ChatResponse
    messages: list[MessageResponse]

class CreateChatRequest(BaseModel):
    title: str = Field(default="Новый чат", min_length=1, max_length=120)

    @field_validator("title")
    @classmethod
    def normalize_name(cls, value: str) -> str:
            value = " ".join(value.split())
            if len(value) < 2:
                raise ValueError("Название чата не может быть пустым")
            return value

class SendMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=8000)
    model_id: str = Field(min_length=1, max_length=255)

    @field_validator("content")
    @classmethod
    def strip_content(cls, value: str) -> str:
        value = value.strip()

        if not value:
             raise ValueError("Сообщение не может быть пустым")

        return value

class SendMessageResponse(BaseModel):
     chat: ChatResponse
     assistant_message: MessageResponse

class ModelResponse(BaseModel):
     id: str
     name: str

def required_chat(chat_id: int, user_id: int, db: Session) -> Chat:
     chat = db.scalar(select(Chat.id == chat_id, Chat.user_id == user_id))

     if not chat:
          raise HTTPException(
               status_code=status.HTTP_404_NOT_FOUND,
               detail="Чат не найден"
          )
     return chat
                      


