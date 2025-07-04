# streamlit_app.py
import streamlit as st
import requests
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Load Gemini API Key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

FASTAPI_URL = "http://localhost:8000" 
st.set_page_config(page_title="TailorTalk")

st.title("TailorTalk")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.chat_input("Ask me to book or cancel an appointment...")
if user_input:
    st.session_state.chat_history.append(("user", user_input))

    # Use Gemini to extract command details
    prompt = f"""
You are a calendar assistant. Analyze this input and extract the following:
1. intent: 'book' or 'cancel'
2. title/summary of the event (if available)
3. datetime (or start/end time)
4. duration in minutes (if given)
5. if 'cancel', provide event title or event_id if known.

Return only JSON format like this:
{{
  "intent": "book",
  "summary": "Meeting with Dr. John",
  "start": "2025-07-04T15:00:00",
  "end": "2025-07-04T15:30:00"
}}
OR
{{
  "intent": "cancel",
  "event_id": "abcdef123456"
}}
User input: \"{user_input}\"
"""

    response = model.generate_content(prompt)
    try:
        parsed = eval(response.text)  # You can use json.loads if it's valid JSON
        if parsed["intent"] == "book":
            res = requests.post(f"{FASTAPI_URL}/book", json=parsed).json()
            reply = f"✅ Event booked: {res.get('event_id')}"
        elif parsed["intent"] == "cancel":
            event_id = parsed.get("event_id")
            if event_id:
                res = requests.delete(f"{FASTAPI_URL}/cancel/{event_id}").json()
                reply = "❌ Event cancelled."
            else:
                reply = "⚠️ Missing event_id for cancellation."
        else:
            reply = "❓ Couldn't understand your intent."
    except Exception as e:
        reply = "⚠️ Sorry, I couldn't parse that. Try being more specific."

    st.session_state.chat_history.append(("ai", reply))

# Display chat history
for role, msg in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(msg)
