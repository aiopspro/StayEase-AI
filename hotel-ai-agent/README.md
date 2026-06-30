# StayEase AI — Intelligent Hotel Booking Agent

An AI-powered hotel booking platform that understands natural language. Users can search for rooms, get intelligent recommendations, and make bookings — all through a conversational chat interface.

Built with **MongoDB Atlas**, **AWS Bedrock (Claude 3)**, **VoyageAI embeddings**, **FastAPI**, and **Streamlit**.

---

## What It Does

| User Says | What Happens |
|---|---|
| "Find deluxe rooms in Goa under $100" | Searches MongoDB with city, type, price filters |
| "I want a romantic room with sea view and pool" | Semantic vector search + Claude generates a personalized recommendation |
| "Book room R005 for Alice" | Validates room exists, creates booking in MongoDB |

---

## Architecture

```
User (Browser)
    │
    ▼
Streamlit UI  (port 8501)
    │  HTTP POST /chat
    ▼
FastAPI Backend  (port 8000)
    │
    ▼
Supervisor Agent
    │
    ├──[intent: search_room]──────▶ Search Agent ──▶ MongoDB (rooms)
    │
    ├──[intent: book_room]────────▶ Booking Agent ──▶ MongoDB (bookings)
    │
    └──[intent: recommend_room]──▶ Recommendation Agent
                                        │
                                        ├──▶ VoyageAI (embed query)
                                        ├──▶ MongoDB (room_vectors) cosine similarity
                                        └──▶ AWS Bedrock Claude (generate response)
```

### Agent Roles

| Agent | File | Responsibility |
|---|---|---|
| Supervisor | `agents/supervisor.py` | Calls Bedrock to classify intent, routes to correct agent |
| Search Agent | `agents/search_agent.py` | Queries MongoDB rooms by city, type, price |
| Booking Agent | `agents/booking_agent.py` | Validates room exists, creates booking record |
| Recommendation Agent | `agents/recommendation_agent.py` | Full RAG — vector search + Claude generation |

### Services

| Service | File | Responsibility |
|---|---|---|
| Bedrock | `services/bedrock.py` | Intent classification + RAG response generation via Claude 3 |
| MongoDB | `services/mongo.py` | Connection to Atlas, exposes rooms/bookings/room_vectors collections |
| Embed | `services/embed.py` | Generates 1024-dim embeddings via VoyageAI voyage-2 model |

---

## RAG Architecture (Recommendation Flow)

This project implements full **Retrieval-Augmented Generation (RAG)**:

```
1. RETRIEVE  — User query is embedded via VoyageAI
               Cosine similarity run against 20 pre-stored room vectors in MongoDB
               Top 3 most relevant rooms selected

2. AUGMENT   — Retrieved room details (name, city, price, amenities, description)
               are formatted into a context block

3. GENERATE  — Context + user query sent to Claude 3 on AWS Bedrock
               Claude writes a warm, conversational recommendation explaining
               WHY each room suits the user — using only retrieved data
```

**Why RAG over keyword search?**
A keyword search for "romantic sea view" would miss rooms described as "ocean facing" or "beachfront". Embeddings capture semantic meaning — so "romantic", "sea view", and "pool" together match rooms that conceptually fit, even with different wording.

---

## Project Structure

```
hotel-ai-agent/
├── agents/
│   ├── supervisor.py           # Intent classification + routing
│   ├── search_agent.py         # MongoDB room search
│   ├── booking_agent.py        # Room booking with validation
│   └── recommendation_agent.py # RAG: vector search + generation
├── services/
│   ├── mongo.py                # MongoDB Atlas connection
│   ├── bedrock.py              # AWS Bedrock Claude (intent + generation)
│   └── embed.py                # VoyageAI embeddings
├── api/
│   └── main.py                 # FastAPI — POST /chat, GET /health
├── ui/
│   └── app.py                  # Streamlit chat interface
├── data/
│   └── rooms.json              # 20 sample hotel rooms (seed data)
├── scripts/
│   ├── seed_rooms.py           # Inserts rooms into MongoDB
│   └── generate_vectors.py     # Generates + stores VoyageAI embeddings
├── .env.example                # Environment variable template
├── requirements.txt
└── README.md
```

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | Streamlit | Chat UI |
| Backend | FastAPI + Uvicorn | REST API |
| Database | MongoDB Atlas | Rooms, bookings, vectors |
| LLM | AWS Bedrock — Claude 3 Sonnet | Intent classification + RAG generation |
| Embeddings | VoyageAI voyage-2 | Semantic vector generation (1024 dims) |
| Similarity | scikit-learn cosine_similarity | Vector matching |
| Language | Python 3.10+ | All services |

---

## Environment Variables

Copy `.env.example` to `.env` and fill in all values:

```env
MONGO_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
VOYAGE_API_KEY=your_voyageai_api_key
API_URL=http://localhost:8000/chat
```

> For server deployment, set `API_URL=http://<SERVER-IP>:8000/chat`

### Where to get each credential

| Variable | Where to get it |
|---|---|
| `MONGO_URI` | MongoDB Atlas → Connect → Drivers → copy connection string |
| `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` | AWS Console → IAM → Users → Create user → Attach `AmazonBedrockFullAccess` → Security credentials → Create access key |
| `AWS_REGION` | Region where Bedrock is available — `us-east-1` recommended |
| `BEDROCK_MODEL_ID` | AWS Console → Bedrock → Model access → Request Claude 3 Sonnet access first |
| `VOYAGE_API_KEY` | voyageai.com → Sign up → API Keys |

---

## Setup & Run

### Step 1 — Install dependencies

```bash
cd hotel-ai-agent
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2 — Check all 3 connections

Run each check individually. All must pass before proceeding.

```bash
# MongoDB
python3 -c "from dotenv import load_dotenv; load_dotenv(); from services.mongo import client; client.admin.command('ping'); print('MongoDB: OK')"

# AWS Bedrock
python3 -c "from dotenv import load_dotenv; load_dotenv(); from services.bedrock import extract_intent; r = extract_intent('Find a room in Goa'); print('Bedrock: OK -', r)"

# VoyageAI
python3 -c "from dotenv import load_dotenv; load_dotenv(); from services.embed import generate_embedding; v = generate_embedding('test'); print('VoyageAI: OK - dims:', len(v))"
```

### Step 3 — Seed room data (run once)

```bash
python3 scripts/seed_rooms.py
```
Expected:
```
Seeded 20 rooms into MongoDB.
Indexes created.
```

### Step 4 — Generate embeddings (run once)

```bash
python3 scripts/generate_vectors.py
```
Expected:
```
Generating embeddings for 20 rooms...
  Embedding R001: Luxury sea-facing deluxe room with pool and wifi...
  ...
Done! Generated 20 embeddings.
```

### Step 5 — Verify data in MongoDB

```bash
python3 -c "
from dotenv import load_dotenv; load_dotenv()
from services.mongo import rooms, room_vectors, bookings
print('Rooms:', rooms.count_documents({}))
print('Vectors:', room_vectors.count_documents({}))
print('Bookings:', bookings.count_documents({}))
"
```
Expected: `Rooms: 20 | Vectors: 20 | Bookings: 0`

### Step 6 — Start the API (Terminal 1)

```bash
uvicorn api.main:app --reload --port 8000
```

### Step 7 — Start the UI (Terminal 2)

```bash
streamlit run ui/app.py
```

Open browser: `http://localhost:8501`

---

## API Reference

**Base URL:** `http://localhost:8000`

### GET /health
Health check.
```bash
curl http://localhost:8000/health
# {"status": "ok"}
```

### POST /chat
Send a message and get a response.

**Request:**
```json
{ "message": "Find deluxe rooms in Goa under $100" }
```

**Response (search_room):**
```json
{
  "intent": "search_room",
  "extracted": { "city": "Goa", "room_type": "Deluxe", "max_price": 100 },
  "results": [ { "room_id": "R001", "hotel_name": "Sea View Resort", ... } ],
  "count": 2
}
```

**Response (recommend_room):**
```json
{
  "intent": "recommend_room",
  "ai_response": "For a romantic getaway with sea views...",
  "recommendations": [ { "room_id": "R001", "similarity_score": 0.8712, ... } ],
  "count": 3
}
```

**Response (book_room):**
```json
{
  "intent": "book_room",
  "booking": {
    "booking_id": "BA3F2C",
    "room_id": "R005",
    "user": "Alice",
    "status": "confirmed",
    "message": "Booking confirmed! Your booking ID is BA3F2C."
  }
}
```

---

## Sample Queries to Try

| Query | Intent Detected | What Happens |
|---|---|---|
| `Find deluxe rooms in Goa` | search_room | Filters by city=Goa, type=Deluxe |
| `Show me budget hotels in Manali under $30` | search_room | Filters by city=Manali, max_price=30 |
| `What rooms are available in Mumbai?` | search_room | Filters by city=Mumbai |
| `I want a romantic room with sea view and pool` | recommend_room | RAG — vector search + Claude response |
| `Suggest a luxury business hotel with conference room` | recommend_room | RAG — vector search + Claude response |
| `Book room R005 for Alice` | book_room | Creates booking after validating room exists |

---

## Data

20 sample hotel rooms across 4 Indian cities:

| City | Rooms | Types |
|---|---|---|
| Goa | R001–R005 | Budget, Standard, Deluxe, Suite |
| Manali | R006–R010 | Budget, Standard, Deluxe, Suite |
| Mumbai | R011–R015 | Budget, Standard, Deluxe, Suite |
| Bangalore | R016–R020 | Budget, Standard, Deluxe, Suite |

MongoDB collections:
- `rooms` — room details (hotel name, city, type, price, amenities)
- `bookings` — confirmed bookings
- `room_vectors` — VoyageAI embeddings for semantic search

---

## Deployment on Ubuntu Server (SSH)

```bash
# 1. Upload project
scp -r hotel-ai-agent ubuntu@<SERVER-IP>:/home/ubuntu/hotel-ai-agent

# 2. On server — install and setup
cd /home/ubuntu/hotel-ai-agent
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 3. Create .env with all 7 variables (set API_URL to server IP)
nano .env

# 4. Run connection checks, seed, generate vectors (Steps 2-5 above)

# 5. Open firewall ports
sudo ufw allow 8000 && sudo ufw allow 8501 && sudo ufw enable

# 6. Start API (background)
nohup uvicorn api.main:app --host 0.0.0.0 --port 8000 > api.log 2>&1 &

# 7. Start UI (background)
nohup streamlit run ui/app.py --server.port 8501 --server.address 0.0.0.0 > ui.log 2>&1 &
```

Access at:
- API: `http://<SERVER-IP>:8000/docs`
- UI: `http://<SERVER-IP>:8501`

---

## Notes

### Problem Solved
Legacy hotel booking systems rely on rigid keyword search — users must know exact room names or filter categories. This project replaces that with natural language understanding and semantic search.

### Key Technical Highlights

1. **Multi-agent architecture** — Supervisor pattern with specialized child agents, each with a single responsibility
2. **Full RAG pipeline** — Not just retrieval: retrieved context is fed into Claude to generate a human-like, personalized response grounded in real data
3. **Semantic search** — VoyageAI voyage-2 embeddings capture meaning, not just keywords — "romantic sea view" matches "ocean facing luxury suite" correctly
4. **Zero hallucination guardrail** — Claude is explicitly instructed to use only the retrieved room data, preventing made-up hotel details
5. **Production-ready structure** — Separated services, agents, API, and UI layers; environment-based config; input validation; graceful error messages

### Flow a Judge Can Follow
```
User types → Bedrock classifies intent → Agent executes →
(for recommendations) VoyageAI embeds → MongoDB vector match →
Bedrock generates natural response → Streamlit renders
```
