# Initial API

An API service that analyzes user queries and returns the most suitable card type with relevant data.

## Features

- Analyzes user queries using OpenAI GPT-4o
- Supports 11 different card types
- RESTful API with automatic documentation
- Configurable environment settings

## Supported Card Types

1. **InfoCard** - General information and explanations
2. **FlightsCard** - Flight search and booking
3. **ShoppingCard** - Product search on various platforms
4. **YelpCard** - Restaurant and local business search
5. **Videos** - Video content search
6. **Images** - Image search
7. **Translation** - Text translation
8. **Conversion** - Unit and currency conversion
9. **ChatCard** - AI chat conversations
10. **Comparison** - Product/item comparisons
11. **PlanningCard** - Planning and organization tasks

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
```
Edit `.env` and add your OpenAI API key.

3. Run the application:
```bash
python run.py
```

Or directly:
```bash
python main.py
```

## Usage

### API Endpoint

**POST** `/initial`

### Request Body
```json
{
    "query": "user query string",
    "screen_content": "optional previous screen data"
}
```

### Response
```json
{
    "query": "user query string",
    "card_list": [
        {
            "card_name": "CardType",
            "card_id": "unique-card-id",
            "data": {
                // Card-specific data structure
            }
        }
    ]
}
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Health Check

- GET `/health` - Returns service health status
- GET `/` - Returns basic service info