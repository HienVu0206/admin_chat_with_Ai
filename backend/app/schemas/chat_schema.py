from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ConversationResponse(BaseModel):
    id: int
    user_name: Optional[str] = None
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True