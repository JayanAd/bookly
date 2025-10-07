from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid
class ReviewModel(BaseModel):
    uid: uuid.UUID
    rating: int = Field(lt=5)
    book_uid: Optional[uuid.UUID]
    user_uid: Optional[uuid.UUID]
    review_text: str
    created_at: datetime
    update_at: datetime

class ReviewCreateModel(BaseModel):
    rating: int = Field(lt=5)
    review_text: str
    
    