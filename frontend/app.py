import streamlit as st
import requests
import uuid
from datetime import datetime

# 🔗 Backend API
BACKEND_URL = "https://rag-backend-961057228920.us-central1.run.app"

# 🎨 Page Setup
st.set_page_config(page_title="RAG Chatbot", page_icon="🤖", layout="wide")

# 🌈 Custom CSS for styling
st.markdown("""
    <style>
    /* General App Styling */
    .stApp {
        background: linear-gradient(to bottom right, #0f2027, #203a43, #2c5364);
        color: white;
    }

    /* Title */
    .title {
        text-align: center;
        font-size: 2.5em;
        color: #00e5ff;
        margin-bottom: 0.2em;
    }

    .subtitle {
        text-align: center;
        font-size: 1.1em;
        color: #b2ebf2;
        margin-bottom: 2em;
    }

    /* Chat bubbles */
    .user-bubble {
        background-color: #1e88e5;
        color: white;
        padding: 0.8em 1em;
        border-radius: 15px;
        margin: 10px 0;
        width: fit-content;
        max-width: 80%;
        align-self: flex-end;
    }

    .assistant-bubble {
        background-color: #263238;
        color: #e0f7fa;
        padding: 0.8em 1em;
        border-radius: 15px;
        margin: 10px 0;
        width: fit-content;
        max-width: 80%;
        align-self: flex-start;
    }

    /* Divider line */
    hr {
        border: 1px solid #00e5ff;
        margin: 20px 0;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(to bottom right, #263238, #37474f);
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# 🧠 Sidebar Section
st.sidebar.title("⚙️ Settings")

# Ask for username
username = st.sidebar.text_input("👤 Enter your name")

# Create persistent session ID
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.sidebar.markdown(f"**🆔 Session ID:** `{st.session_state.session_id}`")
st.sidebar.markdown(f"**⏰ Started:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if st.sidebar.button("🧹 New Session"):
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.sidebar.success("✨ New session started!")

st.sidebar.markdown("---")
st.sidebar.info("Upload your PDFs and start chatting with them!")

# 🧠 Main Title
st.markdown('<h1 class="title">🤖 RAG AI Chat Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Chat with your uploaded documents — powered by FastAPI + Azure OpenAI</p>', unsafe_allow_html=True)

# 📤 File Upload Section
uploaded_files = st.file_uploader("📄 Upload one or more PDFs", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    with st.spinner("⏳ Uploading and processing your PDFs..."):
        try:
            files = [("files", (f.name, f, "application/pdf")) for f in uploaded_files]
            res = requests.post(
                f"{BACKEND_URL}/upload/",
                params={"session_id": st.session_state.session_id},
                files=files,
                timeout=300
            )
            if res.status_code == 200:
                st.success("✅ Files processed successfully! You can now chat below.")
            else:
                st.error(f"❌ Upload failed: {res.text}")
        except Exception as e:
            st.error(f"🚨 Upload error: {e}")

st.markdown("<hr>", unsafe_allow_html=True)

# 💬 Chat UI
if "messages" not in st.session_state:
    st.session_state.messages = []

chat_container = st.container()

for msg in st.session_state.messages:
    role, content = msg["role"], msg["content"]
    if role == "user":
        chat_container.markdown(f"<div class='user-bubble'>{content}</div>", unsafe_allow_html=True)
    else:
        chat_container.markdown(f"<div class='assistant-bubble'>{content}</div>", unsafe_allow_html=True)

if prompt := st.chat_input("💬 Ask something about your PDFs..."):
    st.session_state.messages.append({"role": "user", "content": f"**{username}:** {prompt}"})
    chat_container.markdown(f"<div class='user-bubble'><b>{username}:</b> {prompt}</div>", unsafe_allow_html=True)

    with st.spinner("🤔 Thinking..."):
        try:
            res = requests.post(
                f"{BACKEND_URL}/chat/",
                params={
                    "session_id": st.session_state.session_id,
                    "user_input": prompt
                },
                timeout=300
            )
            if res.status_code == 200:
                data = res.json()
                answer = data.get("answer", "⚠️ No answer received.")
                sources = data.get("sources", [])
                if sources:
                    source_text = "\n\n📚 **Sources:**\n" + "\n".join(
                        [f"- {s.get('filename', '')}" for s in sources]
                    )
                    answer += source_text

                chat_container.markdown(f"<div class='assistant-bubble'>{answer}</div>", unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                st.error(f"❌ API error: {res.text}")
        except Exception as e:
            st.error(f"🚨 Error: {e}")
