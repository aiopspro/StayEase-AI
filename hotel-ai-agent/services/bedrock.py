import os
import json
import boto3
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")

if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
    raise ValueError("AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY must be set in .env")

bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)


def extract_intent(user_message: str) -> dict:
    prompt = f"""You are an intent classifier for a hotel booking system.

Classify the user message into one of these intents:
- search_room: user wants to search/find rooms by city, type, or price
- book_room: user wants to book or reserve a room
- recommend_room: user wants recommendations or suggestions based on preferences

Extract the following fields if present:
- city: the city name mentioned (Goa, Manali, Mumbai, Bangalore)
- room_type: room type (Deluxe, Standard, Suite, Budget)
- room_id: specific room ID if mentioned (e.g. R001)
- max_price: maximum price per night if mentioned
- user: user name if mentioned

User message: "{user_message}"

Respond ONLY with a valid JSON object in this exact format:
{{
  "intent": "search_room|book_room|recommend_room",
  "city": "city name or null",
  "room_type": "room type or null",
  "room_id": "room id or null",
  "max_price": number or null,
  "user": "user name or null"
}}"""

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    })

    response = bedrock.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=body,
    )

    response_body = json.loads(response["body"].read())
    text = response_body["content"][0]["text"].strip()

    # Extract JSON from response
    start = text.find("{")
    end = text.rfind("}") + 1
    json_str = text[start:end]
    return json.loads(json_str)


def generate_response(user_query: str, retrieved_rooms: list) -> str:
    context = ""
    for i, room in enumerate(retrieved_rooms, 1):
        amenities = ", ".join(room.get("amenities", []))
        context += f"""
Room {i}:
- Hotel: {room.get('hotel_name')} ({room.get('city')})
- Type: {room.get('room_type')}
- Price: ${room.get('price')}/night
- Room ID: {room.get('room_id')}
- Amenities: {amenities}
- Description: {room.get('description', '')}
- Match Score: {room.get('similarity_score', 0):.2%}
"""

    prompt = f"""You are a helpful hotel booking assistant.

A user is looking for a hotel room. Based on the rooms retrieved from our database,
give a warm, conversational recommendation explaining WHY each room suits their request.
Do not make up any details — only use the information provided below.

User request: "{user_query}"

Retrieved rooms:
{context}

Write a natural, friendly response recommending these rooms. Explain what makes each
one a good fit for what the user asked for. Mention the Room ID so they can book it.
"""

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    })

    response = bedrock.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=body,
    )

    response_body = json.loads(response["body"].read())
    return response_body["content"][0]["text"].strip()
