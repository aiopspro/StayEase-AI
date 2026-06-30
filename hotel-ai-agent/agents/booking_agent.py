import uuid
from services.mongo import bookings, rooms


def book_room(room_id: str, user: str) -> dict:
    if not rooms.find_one({"room_id": room_id}):
        return {
            "booking_id": None,
            "room_id": room_id,
            "user": user,
            "status": "failed",
            "message": f"Room {room_id} does not exist. Please check the room ID and try again.",
        }

    booking_id = "B" + uuid.uuid4().hex[:6].upper()

    booking_doc = {
        "booking_id": booking_id,
        "room_id": room_id,
        "user": user,
        "status": "confirmed",
    }

    bookings.insert_one(booking_doc)

    return {
        "booking_id": booking_id,
        "room_id": room_id,
        "user": user,
        "status": "confirmed",
        "message": f"Booking confirmed! Your booking ID is {booking_id}.",
    }
