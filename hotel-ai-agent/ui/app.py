import streamlit as st
import requests
import json
import os

API_URL = os.getenv("API_URL", "http://localhost:8000/chat")

st.set_page_config(page_title="StayEase AI", page_icon="🏨", layout="centered")
st.title("🏨 StayEase AI")
st.caption("Your intelligent hotel booking assistant powered by AWS Bedrock & MongoDB Atlas")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask me to find, book, or recommend a hotel room...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(API_URL, json={"message": user_input}, timeout=30)
                response.raise_for_status()
                data = response.json()

                intent = data.get("intent", "unknown")
                reply_lines = []

                if intent == "search_room":
                    results = data.get("results", [])
                    count = data.get("count", 0)
                    if count == 0:
                        reply_lines.append("No rooms found matching your criteria.")
                    else:
                        reply_lines.append(f"Found **{count}** room(s):\n")
                        for r in results:
                            amenities = ", ".join(r.get("amenities", []))
                            reply_lines.append(
                                f"- **{r.get('hotel_name')}** ({r.get('city')}) | "
                                f"{r.get('room_type')} | ${r.get('price')}/night | "
                                f"ID: `{r.get('room_id')}` | Amenities: {amenities}"
                            )

                elif intent == "book_room":
                    booking = data.get("booking", {})
                    reply_lines.append(f"✅ {booking.get('message', 'Booking confirmed!')}")
                    reply_lines.append(f"- **Booking ID:** `{booking.get('booking_id')}`")
                    reply_lines.append(f"- **Room:** `{booking.get('room_id')}`")
                    reply_lines.append(f"- **Guest:** {booking.get('user')}")
                    reply_lines.append(f"- **Status:** {booking.get('status')}")

                elif intent == "recommend_room":
                    recs = data.get("recommendations", [])
                    ai_response = data.get("ai_response", "")
                    count = data.get("count", 0)
                    if count == 0:
                        reply_lines.append("No recommendations found. Try generating vectors first.")
                    else:
                        # Show Claude's natural language response first
                        reply_lines.append(ai_response)

                        # Then show structured room cards below
                        reply_lines.append("\n---\n**Room Details:**")
                        for r in recs:
                            amenities = ", ".join(r.get("amenities", []))
                            score = r.get("similarity_score", 0)
                            reply_lines.append(
                                f"- **{r.get('hotel_name')}** ({r.get('city')}) | "
                                f"{r.get('room_type')} | ${r.get('price')}/night | "
                                f"ID: `{r.get('room_id')}` | Match: {score:.2%} | "
                                f"Amenities: {amenities}"
                            )

                else:
                    reply_lines.append(data.get("message", "Sorry, I couldn't process your request."))

                reply = "\n".join(reply_lines)

                with st.expander("Raw API Response", expanded=False):
                    st.json(data)

            except requests.exceptions.ConnectionError:
                reply = "❌ Cannot connect to the API. Make sure FastAPI is running on port 8000."
            except Exception as e:
                reply = f"❌ Error: {str(e)}"

        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
