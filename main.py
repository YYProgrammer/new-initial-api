from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
from dotenv import load_dotenv

from services.card_selector import CardSelector
from models.request_models import InitialAPIRequest
from models.response_models import InitialAPIResponse

load_dotenv()

app = FastAPI(
    title="Initial API",
    description="API for returning the most suitable card based on user query",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/initial", response_model=InitialAPIResponse)
async def initial_api(
    request: InitialAPIRequest,
    x_brain_user_location: Optional[str] = Header(None, alias="X-Brain-User-Location")
):
    """
    Process user query and return the most suitable card
    """
    try:
        card_selector = CardSelector()
        result = await card_selector.select_card(
            request.query, 
            request.screen_content, 
            user_location=x_brain_user_location
        )
        
        return InitialAPIResponse(
            query=request.query,
            card_list=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Initial API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)