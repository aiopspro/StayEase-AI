import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI is not set in .env")

client = MongoClient(MONGO_URI)
db = client["hotel_modernization"]

rooms = db["rooms"]
bookings = db["bookings"]
room_vectors = db["room_vectors"]
