from services.bedrock import extract_intent
from agents.search_agent import search_rooms
from agents.booking_agent import book_room
from agents.recommendation_agent import recommend_room


def handle_message(user_message: str) -> dict:
    intent_data = extract_intent(user_message)
    intent = intent_data.get("intent", "search_room")

    if intent == "search_room":
        city = intent_data.get("city")
        room_type = intent_data.get("room_type")
        max_price = intent_data.get("max_price")
        results = search_rooms(city=city, room_type=room_type, max_price=max_price)
        return {
            "intent": intent,
            "extracted": intent_data,
            "results": results,
            "count": len(results),
        }

    elif intent == "book_room":
        room_id = intent_data.get("room_id") or "R001"
        user = intent_data.get("user") or "Guest"
        result = book_room(room_id=room_id, user=user)
        return {
            "intent": intent,
            "extracted": intent_data,
            "booking": result,
        }

    elif intent == "recommend_room":
        result = recommend_room(query=user_message)
        return {
            "intent": intent,
            "extracted": intent_data,
            "recommendations": result["rooms"],
            "ai_response": result["response"],
            "count": len(result["rooms"]),
        }

    else:
        return {
            "intent": "unknown",
            "extracted": intent_data,
            "message": "I couldn't understand your request. Try asking to search, book, or get recommendations for rooms.",
        }
