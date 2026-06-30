import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from services.mongo import rooms, db

ROOMS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "rooms.json")


def seed():
    with open(ROOMS_FILE, "r") as f:
        data = json.load(f)

    rooms.drop()
    result = rooms.insert_many(data)
    print(f"Seeded {len(result.inserted_ids)} rooms into MongoDB.")

    # Create indexes
    rooms.create_index("room_id", unique=True)
    rooms.create_index("city")
    rooms.create_index("room_type")
    rooms.create_index("price")
    print("Indexes created.")


if __name__ == "__main__":
    seed()
