import streamlit as st
from streamlit_chat import message
import os
import requests
import time
from dotenv import load_dotenv

# ----------------------------
# Load environment variables
# ----------------------------
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ----------------------------
# Streamlit Page Configuration
# ----------------------------
st.set_page_config(page_title="TalentScout AI - Hiring Assistant", page_icon="🧠", layout="centered")

# ----------------------------
# Custom CSS Styling
# ----------------------------
st.markdown("""
    <style>
    body {
        background-color: #f5f7fa;
    }
    .stChatInputContainer {
        background: #fff;
        border-top: 2px solid #ccc;
    }
    .stButton button {
        background-color: #003366;
        color: white;
        font-weight: bold;
        border-radius: 8px;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #003366;
    }
    .chat-container {
        background-color: #ffffff;
        padding: 1.2rem;
        border-radius: 12px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
        margin-top: 1rem;
    }
    .info-box {
        background-color: #eaf3ff;
        padding: 0.8rem;
        border-radius: 10px;
        margin-bottom: 10px;
        font-size: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------------------
# App Header
# ----------------------------
st.markdown("## 🧠 TalentScout AI Assistant")
st.caption("Your intelligent virtual recruiter for smarter hiring decisions.")

# ----------------------------
# State Initialization
# ----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "stage" not in st.session_state:
    st.session_state.stage = "greeting"
if "candidate_info" not in st.session_state:
    st.session_state.candidate_info = {}
if "tech_questions" not in st.session_state:
    st.session_state.tech_questions = []
if "end_chat" not in st.session_state:
    st.session_state.end_chat = False

# ----------------------------
# LLM Response (Groq only)
# ----------------------------
def generate_llm_response(prompt):
    try:
        with st.spinner("Thinking..."):
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": prompt}]
            }
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("Groq error:", e)
        return "⚠️ Groq API request failed. Please check your API key or try again later."

# ----------------------------
# Generate 9 Tiered Questions
# ----------------------------
def get_technical_questions(tech_stack):
    prompt = f"""
You are an expert technical interviewer.

Generate 3 basic, 3 intermediate, and 3 advanced (pro-level) coding interview questions for the following technologies:
{tech_stack}

Format:
[Basic] ...
[Intermediate] ...
[Advanced] ...
"""
    return generate_llm_response(prompt)

# ----------------------------
# Chat Logic
# ----------------------------
def chat_logic(user_input):
    info = st.session_state.candidate_info
    stage = st.session_state.stage

    if user_input.lower() in ["exit", "quit", "bye", "end"]:
        st.session_state.end_chat = True
        return "✅ Thank you for chatting with TalentScout! We’ll be in touch shortly. Goodbye! 👋"

    if stage == "greeting":
        st.session_state.stage = "full_name"
        return "👋 Welcome! I’m your virtual assistant from TalentScout.\n\nCan I know your **full name**?"

    elif stage == "full_name":
        info["Full Name"] = user_input
        st.session_state.stage = "email"
        return "📧 What’s your **email address**?"

    elif stage == "email":
        info["Email"] = user_input
        st.session_state.stage = "phone"
        return "📞 Could you share your **phone number**?"

    elif stage == "phone":
        info["Phone"] = user_input
        st.session_state.stage = "experience"
        return "🧑‍💻 How many **years of experience** do you have?"

    elif stage == "experience":
        info["Experience"] = user_input
        st.session_state.stage = "position"
        return "🎯 What **position(s)** are you applying for?"

    elif stage == "position":
        info["Position"] = user_input
        st.session_state.stage = "location"
        return "📍 Where are you **currently located**?"

    elif stage == "location":
        info["Location"] = user_input
        st.session_state.stage = "tech_stack"
        return "💻 Please list your **tech stack** (e.g., Python, React, MongoDB)..."

    elif stage == "tech_stack":
        info["Tech Stack"] = user_input
        st.session_state.stage = "answering"
        tech_q = get_technical_questions(user_input)
        st.session_state.tech_questions = tech_q.split("\n")
        return f"🧪 Here are 9 questions based on your tech stack:\n\n{tech_q}\n\n👉 Reply with anything to see the answers."

    elif stage == "answering":
        st.session_state.stage = "done"
        questions = "\n".join(st.session_state.tech_questions)
        prompt = f"""You are a senior software engineer. Provide accurate and concise answers to the following questions:\n\n{questions}"""
        return generate_llm_response(prompt)

    else:
        return "❓ Hmm, I didn’t quite get that. Could you please rephrase?"

# ----------------------------
# Chat Display
# ----------------------------
with st.container():
    for i, msg in enumerate(st.session_state.messages):
        message(msg["content"], is_user=msg["role"] == "user", key=str(i))

# ----------------------------
# Chat Input
# ----------------------------
if not st.session_state.end_chat:
    user_prompt = st.chat_input("Type here to talk to TalentScout...")

    if user_prompt:
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        bot_response = chat_logic(user_prompt)
        time.sleep(0.2)
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        st.rerun()
else:
    st.success("Conversation has ended. Refresh the page to restart.")
    with st.expander("📄 Candidate Summary"):
        for k, v in st.session_state.candidate_info.items():
            st.markdown(f"**{k}:** {v}")
