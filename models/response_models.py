from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class CardData(BaseModel):
    card_name: str
    card_id: str
    data: Dict[str, Any]

class InitialAPIResponse(BaseModel):
    query: str
    card_list: List[CardData]