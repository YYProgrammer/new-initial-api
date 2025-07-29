import openai
import os
from typing import Optional
import json
from .screen_content_processor import ScreenContentProcessor

class OpenAIService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.test_mode = api_key == "OPENAI_API_KEY" or not api_key
        self.screen_processor = ScreenContentProcessor()
        
        if not self.test_mode:
            # Use Cerebras proxy endpoint instead of OpenAI
            self.client = openai.AsyncOpenAI(
                api_key="DlJYSkMVj1x4zoe8jZnjvxfHG6z5yGxK",
                base_url="https://cerebras-proxy.brain.loocaa.com:1443/v1"
            )
        else:
            print("Running in test mode - no real API calls will be made")
    
    async def analyze_query(self, query: str, screen_content: Optional[str] = None) -> dict:
        """
        Analyze user query and screen content to determine the most suitable card type
        """
        system_prompt = """
You are an AI assistant that analyzes user queries and determines the most suitable card type to display.

Available card types:
- InfoCard: For general information, explanations, or when user wants to learn about something
- FlightsCard: For flight searches, travel booking inquiries
- ShoppingCard: For product searches, shopping inquiries
- YelpCard: For restaurant searches, local business inquiries
- Videos: For video content searches
- Images: For image searches
- Translation: For translation requests
- Conversion: For unit conversions, currency conversions
- ChatCard: For general conversation, when user wants to chat
- Comparison: For comparing two items/products
- PlanningCard: For planning tasks like trip planning, project planning

IMPORTANT SCREEN CONTENT ANALYSIS:
When screen content is provided, analyze it carefully to extract relevant information:

1. For queries like "help me buy the product" or "I want to purchase this":
   - Look for product names, brand names, or items mentioned in the screen content
   - Use the extracted product name as the "search_query" for ShoppingCard
   - Example: If screen shows "拉布布" in a conversation, use "拉布布" as search_query

2. For queries like "please introduce him/her" or "tell me about this person":
   - Look for person names, titles, or biographical information in the screen content
   - Use the extracted name/topic as the "query" for InfoCard
   - Example: If screen shows "Michael Jordan", use "Michael Jordan" as query

3. For other queries, extract contextually relevant information from screen content

Based on the user query and optional screen content, determine:
1. The most suitable card type
2. Extract relevant parameters for that card type (prioritizing screen content information)
3. Provide reasoning for the choice

Return your response as a JSON object with the following structure:
{
    "card_type": "CardName",
    "parameters": {...},
    "reasoning": "explanation"
}

IMPORTANT: For FlightsCard, use these exact parameter names:
- "departure_location": departure airport/city
- "arrival_location": destination airport/city  
- "trip_start_date": departure date
- "trip_end_date": return date (null for one-way)
- "adults": number of adults (default 1)
- "children": number of children (default 0)
- "infants": number of infants (default 0)
- "flight_class": "ECONOMY"/"BUSINESS"/"FIRST_CLASS" (default "ECONOMY")

For ShoppingCard, use these exact parameter names:
- "search_query": product search keywords (extracted from screen content when available)
- "platforms": shopping platform (e.g. "Amazon")
- "gender": "all_gender" by default
- "brands": brand name if specified

For InfoCard, use these exact parameter names:
- "query": the topic/subject to provide information about (extracted from screen content when available)

For Translation, use these exact parameter names:
- "input_text": text to translate
- "input_language": source language
- "output_language": target language
- "output_text": translated result (optional)
"""
        
        from datetime import datetime
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_day = datetime.now().strftime("%A")
        
        user_content = f"Query: {query}\nCurrent Date: {current_date} ({current_day})"
        if screen_content:
            # Process screen content to extract meaningful information
            screen_summary = self.screen_processor.get_context_summary(screen_content)
            user_content += f"\n{screen_summary}"
        
        if self.test_mode:
            return self._get_test_response(query, screen_content)
            
        try:
            response = await self.client.chat.completions.create(
                model="qwen-3-235b-a22b-instruct-2507",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            print(f"OpenAI response content: {content}")
            
            # Handle JSON code blocks
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            return json.loads(content)
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return {
                "card_type": "InfoCard",
                "parameters": {"query": query},
                "reasoning": "Default fallback due to API error"
            }
    
    def _get_test_response(self, query: str, screen_content: Optional[str] = None) -> dict:
        """
        Generate test responses for demonstration without calling OpenAI API
        """
        query_lower = query.lower()
        
        # Handle specific test cases with screen content
        if screen_content:
            # Extract meaningful content from screen
            extracted_texts = self.screen_processor.extract_text_content(screen_content)
            
            # Shopping case: "help me buy the product"
            if query_lower == "help me buy the product":
                # Look for product names in extracted text, prioritizing short product names
                product_candidates = []
                for text_item in extracted_texts:
                    text = text_item['text'].strip()
                    
                    # Skip if too long (likely full sentences) or too short
                    if len(text) < 2 or len(text) > 10:
                        continue
                        
                    # Look for Chinese product names or specific words
                    if any('\u4e00' <= char <= '\u9fff' for char in text):
                        # Extract product name from questions like "你知道拉布布吗"
                        if '吗' in text and len(text.replace('你知道', '').replace('吗', '').strip()) > 1:
                            product_name = text.replace('你知道', '').replace('吗', '').strip()
                            product_candidates.append(product_name)
                        elif not any(word in text for word in ['你', '我', '他', '她', '吗', '呢', '的']):
                            # Direct product names without question words
                            product_candidates.append(text)
                
                if product_candidates:
                    # Use the shortest candidate as it's likely the product name
                    best_product = min(product_candidates, key=len)
                    return {
                        "card_type": "ShoppingCard",
                        "parameters": {
                            "search_query": best_product,
                            "platforms": "Amazon",
                            "gender": "all_gender",
                            "brands": None
                        },
                        "reasoning": f"User wants to buy product '{best_product}' found in screen content"
                    }
            
            # Info case: "please introduce him"
            elif query_lower == "please introduce him":
                # Look for person names, prioritizing recognizable names
                name_candidates = []
                
                for text_item in extracted_texts:
                    text = text_item['text'].strip()
                    
                    # Skip very short or very long texts
                    if len(text) < 3 or len(text) > 50:
                        continue
                    
                    # Look for specific names or keywords
                    text_lower = text.lower()
                    
                    # Check for Michael Jordan specific references
                    if any(keyword in text_lower for keyword in ['jordan', 'michael', '乔丹', '迈克尔']):
                        name_candidates.append("michael jordan")
                        break
                    
                    # Check for Chinese names (typically 2-4 characters)
                    if (any('\u4e00' <= char <= '\u9fff' for char in text) and 
                        2 <= len(text) <= 4 and
                        not any(word in text for word in ['百科', '词条', '编辑', '维护', '指南'])):
                        name_candidates.append(text)
                    
                    # Check for English names (First Last pattern)
                    if (text.replace(' ', '').isalpha() and 
                        len(text.split()) == 2 and
                        all(word.istitle() for word in text.split())):
                        name_candidates.append(text)
                
                if name_candidates:
                    # Prioritize "michael jordan" if found, otherwise use first candidate
                    best_name = "michael jordan" if "michael jordan" in name_candidates else name_candidates[0]
                    return {
                        "card_type": "InfoCard",
                        "parameters": {
                            "query": best_name
                        },
                        "reasoning": f"User wants information about '{best_name}' found in screen content"
                    }
                
                # Fallback for introduce queries
                return {
                    "card_type": "InfoCard",
                    "parameters": {
                        "query": "michael jordan"
                    },
                    "reasoning": "User wants to know about a person, defaulting to Michael Jordan"
                }
        
        # Flight-related queries
        if any(word in query_lower for word in ["flight", "fly", "book", "airport", "sfo", "lax"]):
            return {
                "card_type": "FlightsCard",
                "parameters": {
                    "departure_location": "SFO",
                    "arrival_location": "LAX",
                    "adults": 1,
                    "children": 0,
                    "infants": 0,
                    "flight_class": "ECONOMY"
                },
                "reasoning": "User is looking for flight information"
            }
        
        # Shopping queries
        elif any(word in query_lower for word in ["buy", "shop", "purchase", "amazon", "iphone", "product"]):
            return {
                "card_type": "ShoppingCard",
                "parameters": {
                    "search_query": "iPhone" if "iphone" in query_lower else "smartphone",
                    "platforms": "Amazon"
                },
                "reasoning": "User wants to shop for products"
            }
        
        # Translation queries
        elif any(word in query_lower for word in ["translate", "translation", "chinese", "spanish", "french"]):
            return {
                "card_type": "Translation",
                "parameters": {
                    "input_text": "hello",
                    "input_language": "English",
                    "output_language": "Chinese"
                },
                "reasoning": "User needs translation services"
            }
        
        # Restaurant/food queries
        elif any(word in query_lower for word in ["restaurant", "food", "eat", "dining", "yelp"]):
            return {
                "card_type": "YelpCard",
                "parameters": {
                    "keyword": "restaurant",
                    "location": "San Francisco"
                },
                "reasoning": "User is looking for restaurants"
            }
        
        # Video queries
        elif any(word in query_lower for word in ["video", "watch", "youtube", "movie"]):
            return {
                "card_type": "Videos",
                "parameters": {
                    "topic": "entertainment"
                },
                "reasoning": "User wants to find videos"
            }
        
        # Image queries
        elif any(word in query_lower for word in ["image", "picture", "photo"]):
            return {
                "card_type": "Images",
                "parameters": {
                    "topic": "nature"
                },
                "reasoning": "User is looking for images"
            }
        
        # Conversion queries
        elif any(word in query_lower for word in ["convert", "conversion", "currency", "usd", "eur"]):
            return {
                "card_type": "Conversion",
                "parameters": {
                    "input_value": "100",
                    "input_unit": "USD",
                    "output_unit": "EUR"
                },
                "reasoning": "User needs unit conversion"
            }
        
        # Chat queries
        elif any(word in query_lower for word in ["chat", "talk", "conversation", "hi", "hello"]):
            return {
                "card_type": "ChatCard",
                "parameters": {
                    "query": query
                },
                "reasoning": "User wants to have a conversation"
            }
        
        # Comparison queries
        elif any(word in query_lower for word in ["compare", "comparison", "vs", "versus"]):
            return {
                "card_type": "Comparison",
                "parameters": {
                    "item_1": "iPhone 14",
                    "item_2": "iPhone 15"
                },
                "reasoning": "User wants to compare items"
            }
        
        # Planning queries
        elif any(word in query_lower for word in ["plan", "planning", "schedule", "trip", "organize"]):
            return {
                "card_type": "PlanningCard",
                "parameters": {
                    "query": query
                },
                "reasoning": "User needs planning assistance"
            }
        
        # Default to InfoCard
        else:
            return {
                "card_type": "InfoCard",
                "parameters": {
                    "query": query
                },
                "reasoning": "General information request"
            }