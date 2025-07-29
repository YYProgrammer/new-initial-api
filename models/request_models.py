from pydantic import BaseModel
from typing import Optional

class InitialAPIRequest(BaseModel):
    query: str
    screen_content: Optional[str] = None