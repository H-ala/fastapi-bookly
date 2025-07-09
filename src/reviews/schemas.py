from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid

# this  model helps us serialize a review obj
class ReviewModel(BaseModel):
    uid: uuid.UUID
    rating: int = Field(lt=6, gt=0) # lt(lower than), gt(greater than)
    review_text: str # this means this field is simply a string and it will not be nullable
    user_uid: Optional[uuid.UUID]
    book_uid: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime

class ReviewCreateModel(BaseModel):
    rating: int = Field(lt=6, gt=0)
    review_text: str