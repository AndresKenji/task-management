from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    done: Optional[bool] = None

class TaskShow(TaskBase):
    id: int
    done: bool
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True