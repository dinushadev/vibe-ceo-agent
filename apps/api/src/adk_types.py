
from pydantic import BaseModel
from typing import List, Optional

class Part(BaseModel):
    text: str

class Content(BaseModel):
    role: str
    parts: List[Part]
