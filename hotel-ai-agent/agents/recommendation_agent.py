import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from services.mongo import room_vectors, rooms
from services.embed import generate_embedding
from services.bedrock import generate_response


def recommend_room(query: str) -> dict:
    query_embedding = generate_embedding(query)
    query_vec = np.array(query_embedding).reshape(1, -1)

    vectors = list(room_vectors.find({}, {"_id": 0}))

    if not vectors:
        return {"rooms": [], "response": "No rooms found in the database."}

    scored = []
    for v in vectors:
        if not v.get("embedding"):
            continue
        room_vec = np.array(v["embedding"]).reshape(1, -1)
        score = cosine_similarity(query_vec, room_vec)[0][0]
        scored.append({"room_id": v["room_id"], "description": v.get("description", ""), "score": float(score)})

    scored.sort(key=lambda x: x["score"], reverse=True)
    top3 = scored[:3]

    retrieved_rooms = []
    for item in top3:
        room = rooms.find_one({"room_id": item["room_id"]}, {"_id": 0})
        if room:
            room["similarity_score"] = round(item["score"], 4)
            room["description"] = item["description"]
            retrieved_rooms.append(room)

    # RAG: Generation step — feed retrieved rooms into Claude for a natural response
    ai_response = generate_response(query, retrieved_rooms)

    return {
        "rooms": retrieved_rooms,
        "response": ai_response,
    }
