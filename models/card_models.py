from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class InfoCardData(BaseModel):
    query: str

class FlightSuggestion(BaseModel):
    departure_location: str
    arrival_location: str
    trip_start_date: str
    trip_end_date: Optional[str]
    adults: int
    children: int
    infants: int
    flight_class: str
    reason: str

class FlightsCardData(BaseModel):
    departure_location: str
    arrival_location: str
    trip_start_date: str
    trip_end_date: Optional[str]
    adults: int
    children: int
    infants: int
    flight_class: str
    suggestions: Optional[List[FlightSuggestion]]

class ShoppingCardData(BaseModel):
    search_query: str
    platforms: str
    gender: Optional[str] = "all_gender"
    brands: Optional[str]

class YelpCardData(BaseModel):
    keyword: str
    location: str
    categories: List[str]

class VideosCardData(BaseModel):
    topic: str

class ImagesCardData(BaseModel):
    topic: str

class TranslationCardData(BaseModel):
    input_text: str
    input_language: str
    output_language: str
    output_text: Optional[str]

class ConversionCardData(BaseModel):
    input_value: str
    input_unit: str
    output_unit: str

class ChatCardData(BaseModel):
    query: str

class ComparisonCardData(BaseModel):
    item_1: str
    item_2: str

class PlanningCardData(BaseModel):
    query: str
    screen_content: Optional[str]