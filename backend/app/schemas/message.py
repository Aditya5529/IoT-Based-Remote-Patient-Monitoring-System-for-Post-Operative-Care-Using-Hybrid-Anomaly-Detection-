from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    recipient_id: UUID

class MessageRead(MessageBase):
    id: UUID
    sender_id: UUID
    recipient_id: UUID
    timestamp: datetime
    read: bool
    
    # Optional sender info for UI
    sender_name: Optional[str] = None 

    class Config:
        from_attributes = True
