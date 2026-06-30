from services.mongo import rooms


def search_rooms(city: str = None, room_type: str = None, max_price: float = None) -> list:
    query = {}

    if city:
        query["city"] = {"$regex": city, "$options": "i"}
    if room_type:
        query["room_type"] = {"$regex": room_type, "$options": "i"}
    if max_price is not None:
        query["price"] = {"$lte": max_price}

    results = list(rooms.find(query, {"_id": 0}))
    return results
