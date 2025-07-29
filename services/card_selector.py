import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from services.openai_service import OpenAIService
from models.response_models import CardData
from models.card_models import *

class CardSelector:
    def __init__(self):
        self.openai_service = OpenAIService()
    
    async def select_card(self, query: str, screen_content: Optional[str] = None, user_location: Optional[str] = None) -> List[CardData]:
        """
        Select the most suitable card based on user query, screen content, and user location
        """
        # Analyze query using OpenAI
        analysis = await self.openai_service.analyze_query(query, screen_content)
        
        card_type = analysis.get("card_type", "InfoCard")
        parameters = analysis.get("parameters", {})
        
        # Generate card based on type
        card_data = self._generate_card_data(card_type, parameters, query, screen_content, user_location)
        
        return [card_data]
    
    def _generate_card_data(self, card_type: str, parameters: Dict[str, Any], 
                          query: str, screen_content: Optional[str], user_location: Optional[str] = None) -> CardData:
        """
        Generate card data based on card type and parameters
        """
        card_id = f"card-{str(uuid.uuid4())}"
        
        if card_type == "InfoCard":
            return CardData(
                card_name="InfoCard",
                card_id=card_id,
                data=self._generate_info_card_data(parameters, query)
            )
        elif card_type == "FlightsCard":
            return CardData(
                card_name="FlightsCard",
                card_id=card_id,
                data=self._generate_flights_card_data(parameters, query, user_location)
            )
        elif card_type == "ShoppingCard":
            return CardData(
                card_name="ShoppingSearchResults",
                card_id=card_id,
                data=self._generate_shopping_card_data(parameters, query)
            )
        elif card_type == "YelpCard":
            return CardData(
                card_name="YelpCard",
                card_id=card_id,
                data=self._generate_yelp_card_data(parameters, query)
            )
        elif card_type == "Videos":
            return CardData(
                card_name="Videos",
                card_id=card_id,
                data=self._generate_videos_card_data(parameters, query)
            )
        elif card_type == "Images":
            return CardData(
                card_name="Images",
                card_id=card_id,
                data=self._generate_images_card_data(parameters, query)
            )
        elif card_type == "Translation":
            return CardData(
                card_name="Translation",
                card_id=card_id,
                data=self._generate_translation_card_data(parameters, query)
            )
        elif card_type == "Conversion":
            return CardData(
                card_name="Conversion",
                card_id=card_id,
                data=self._generate_conversion_card_data(parameters, query)
            )
        elif card_type == "ChatCard":
            return CardData(
                card_name="ChatCard",
                card_id=card_id,
                data=self._generate_chat_card_data(parameters, query)
            )
        elif card_type == "Comparison":
            return CardData(
                card_name="Comparison",
                card_id=card_id,
                data=self._generate_comparison_card_data(parameters, query)
            )
        elif card_type == "PlanningCard":
            return CardData(
                card_name="PlanningCard",
                card_id=card_id,
                data=self._generate_planning_card_data(parameters, query, screen_content)
            )
        else:
            # Default to InfoCard
            return CardData(
                card_name="InfoCard",
                card_id=card_id,
                data=self._generate_info_card_data(parameters, query)
            )
    
    def _generate_info_card_data(self, parameters: Dict[str, Any], query: str) -> Dict:
        return {"query": parameters.get("query", query)}
    
    def _generate_flights_card_data(self, parameters: Dict[str, Any], query: str, user_location: Optional[str] = None) -> Dict:
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        
        # Extract departure and arrival locations with better mapping
        departure = parameters.get("departure_location", "")
        arrival = parameters.get("arrival_location", "")
        
        # Handle alternative parameter names from OpenAI response
        if not departure:
            departure = parameters.get("departure_airport", "")
        if not arrival:
            arrival = parameters.get("arrival_airport", "")
        
        # Use user_location as default departure if no departure location found
        if not departure and user_location:
            departure = user_location
        elif not departure:
            departure = "SFO"  # Final fallback
        
        # Handle trip_start_date with past date validation
        trip_start_date = parameters.get("trip_start_date") or tomorrow
        trip_start_date = self._validate_future_date(trip_start_date, tomorrow)
            
        data = {
            "departure_location": departure,
            "arrival_location": arrival if arrival else "SFO",  # Only default if empty
            "trip_start_date": trip_start_date,
            "trip_end_date": parameters.get("trip_end_date"),
            "adults": parameters.get("adults", 1),
            "children": parameters.get("children", 0),
            "infants": parameters.get("infants", 0),
            "flight_class": parameters.get("flight_class", "ECONOMY"),
            "suggestions": parameters.get("suggestions")
        }
        
        # Generate suggestions if required parameters are missing
        if not data["departure_location"] and not data["suggestions"]:
            data["suggestions"] = [{
                "departure_location": "SFO",
                "arrival_location": "LAX",
                "trip_start_date": tomorrow,
                "trip_end_date": None,
                "adults": 1,
                "children": 0,
                "infants": 0,
                "flight_class": "ECONOMY",
                "reason": "Popular destination with many flight options."
            }]
        
        return data
    
    def _generate_shopping_card_data(self, parameters: Dict[str, Any], query: str) -> Dict:
        return {
            "search_query": parameters.get("search_query", "Natural Phone"),
            "platforms": parameters.get("platforms", "Amazon"),
            "gender": parameters.get("gender", "all_gender"),
            "brands": parameters.get("brands")
        }
    
    def _generate_yelp_card_data(self, parameters: Dict[str, Any], query: str) -> Dict:
        return {
            "keyword": parameters.get("keyword", "restaurant"),
            "location": parameters.get("location", "San Francisco"),
            "categories": ["restaurants", "food", "pub", "pubs"]
        }
    
    def _generate_videos_card_data(self, parameters: Dict[str, Any], query: str) -> Dict:
        return {"topic": parameters.get("topic", "Popular")}
    
    def _generate_images_card_data(self, parameters: Dict[str, Any], query: str) -> Dict:
        return {"topic": parameters.get("topic", "Popular")}
    
    def _generate_translation_card_data(self, parameters: Dict[str, Any], query: str) -> Dict:
        return {
            "input_text": parameters.get("input_text", query),
            "input_language": parameters.get("input_language", "English"),
            "output_language": parameters.get("output_language", "English"),
            "output_text": parameters.get("output_text")
        }
    
    def _generate_conversion_card_data(self, parameters: Dict[str, Any], query: str) -> Dict:
        return {
            "input_value": parameters.get("input_value", "1"),
            "input_unit": parameters.get("input_unit", "USD"),
            "output_unit": parameters.get("output_unit", "EUR")
        }
    
    def _generate_chat_card_data(self, parameters: Dict[str, Any], query: str) -> Dict:
        return {"query": parameters.get("query", query)}
    
    def _generate_comparison_card_data(self, parameters: Dict[str, Any], query: str) -> Dict:
        return {
            "item_1": parameters.get("item_1", "iPhone 14"),
            "item_2": parameters.get("item_2", "iPhone 15")
        }
    
    def _generate_planning_card_data(self, parameters: Dict[str, Any], 
                                   query: str, screen_content: Optional[str]) -> Dict:
        return {
            "query": query,
            "screen_content": screen_content or ""
        }
    
    def _validate_future_date(self, date_str: str, default_date: str) -> str:
        """
        Validate that the date is not in the past. If it is, return default_date.
        Handles various date formats and adjusts past dates to future equivalents.
        """
        try:
            import re
            from dateutil import parser
            
            # If it's already our default tomorrow format, return as is
            if re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', date_str):
                parsed_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            else:
                # Try to parse various date formats
                parsed_date = parser.parse(date_str, fuzzy=True)
            
            current_date = datetime.now()
            
            # If the parsed date is in the past, we need to adjust it
            if parsed_date.date() < current_date.date():
                # For relative dates like "next Friday", find the next occurrence
                if "friday" in date_str.lower():
                    days_until_friday = (4 - current_date.weekday()) % 7  # Friday is weekday 4
                    if days_until_friday == 0:  # If today is Friday, get next Friday
                        days_until_friday = 7
                    next_friday = current_date + timedelta(days=days_until_friday)
                    return next_friday.strftime("%Y-%m-%d %H:%M:%S")
                elif "monday" in date_str.lower():
                    days_until_monday = (0 - current_date.weekday()) % 7  # Monday is weekday 0
                    if days_until_monday == 0:
                        days_until_monday = 7
                    next_monday = current_date + timedelta(days=days_until_monday)
                    return next_monday.strftime("%Y-%m-%d %H:%M:%S")
                elif "tuesday" in date_str.lower():
                    days_until_tuesday = (1 - current_date.weekday()) % 7
                    if days_until_tuesday == 0:
                        days_until_tuesday = 7
                    next_tuesday = current_date + timedelta(days=days_until_tuesday)
                    return next_tuesday.strftime("%Y-%m-%d %H:%M:%S")
                elif "wednesday" in date_str.lower():
                    days_until_wednesday = (2 - current_date.weekday()) % 7
                    if days_until_wednesday == 0:
                        days_until_wednesday = 7
                    next_wednesday = current_date + timedelta(days=days_until_wednesday)
                    return next_wednesday.strftime("%Y-%m-%d %H:%M:%S")
                elif "thursday" in date_str.lower():
                    days_until_thursday = (3 - current_date.weekday()) % 7
                    if days_until_thursday == 0:
                        days_until_thursday = 7
                    next_thursday = current_date + timedelta(days=days_until_thursday)
                    return next_thursday.strftime("%Y-%m-%d %H:%M:%S")
                elif "saturday" in date_str.lower():
                    days_until_saturday = (5 - current_date.weekday()) % 7
                    if days_until_saturday == 0:
                        days_until_saturday = 7
                    next_saturday = current_date + timedelta(days=days_until_saturday)
                    return next_saturday.strftime("%Y-%m-%d %H:%M:%S")
                elif "sunday" in date_str.lower():
                    days_until_sunday = (6 - current_date.weekday()) % 7
                    if days_until_sunday == 0:
                        days_until_sunday = 7
                    next_sunday = current_date + timedelta(days=days_until_sunday)
                    return next_sunday.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    # For other past dates, use default
                    return default_date
            
            # If date is in the future, return in our standard format
            return parsed_date.strftime("%Y-%m-%d %H:%M:%S")
            
        except Exception as e:
            print(f"Date parsing error: {e}")
            return default_date