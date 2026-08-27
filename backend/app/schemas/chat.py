from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ChatRequest(BaseModel):
    content: str
    conversation_id: int | None = None

class ChatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: int
    role: str
    content: str
    created_at: datetime
