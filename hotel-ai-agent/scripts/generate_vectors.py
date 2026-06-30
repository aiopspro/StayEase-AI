import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.mongo import rooms, room_vectors
from services.embed import generate_embedding


DESCRIPTIONS = {
    "R001": "Luxury sea-facing deluxe room with pool and wifi in Goa",
    "R002": "Premium suite with spa, pool, and gym at Beach Paradise Hotel in Goa",
    "R003": "Cozy standard room with breakfast at Sunrise Inn Goa",
    "R004": "Affordable budget room with wifi near Goa beach",
    "R005": "Deluxe room with gym and restaurant at Goa Grand Hotel",
    "R006": "Mountain view deluxe room with fireplace and breakfast in Manali",
    "R007": "Luxury Himalayan suite with spa, fireplace, and gym in Manali",
    "R008": "Comfortable standard room with mountain view and breakfast in Manali",
    "R009": "Budget lodge with wifi surrounded by alpine scenery in Manali",
    "R010": "Deluxe room with fireplace and pool at Snowflake Hotel Manali",
    "R011": "Premium sea-view suite with spa and pool on Marine Drive Mumbai",
    "R012": "Business deluxe room with gym and conference room in Mumbai",
    "R013": "Standard room with breakfast at Mumbai Central Inn",
    "R014": "Budget room with wifi in central Mumbai",
    "R015": "Deluxe harbour view room with pool and gym in Mumbai",
    "R016": "Luxury suite with pool, spa, and conference room in Bangalore tech hub",
    "R017": "Deluxe business room with gym and restaurant near tech park Bangalore",
    "R018": "Comfortable garden view standard room with breakfast in Bangalore",
    "R019": "Affordable budget lodge with wifi in Bangalore startup district",
    "R020": "Deluxe rooftop room with pool and restaurant on MG Road Bangalore",
}


def generate_vectors():
    all_rooms = list(rooms.find({}, {"_id": 0}))

    room_vectors.drop()
    print(f"Generating embeddings for {len(all_rooms)} rooms...")

    for room in all_rooms:
        room_id = room["room_id"]
        description = DESCRIPTIONS.get(
            room_id,
            f"{room['room_type']} room at {room['hotel_name']} in {room['city']} "
            f"with amenities: {', '.join(room.get('amenities', []))}"
        )

        print(f"  Embedding {room_id}: {description[:60]}...")
        embedding = generate_embedding(description)

        room_vectors.insert_one({
            "room_id": room_id,
            "description": description,
            "embedding": embedding,
        })

    room_vectors.create_index("room_id", unique=True)
    print(f"Done! Generated {len(all_rooms)} embeddings.")


if __name__ == "__main__":
    generate_vectors()
