import streamlit as st
import requests
import uuid

# ===========================
# 🎨 Custom Styling & Theme
# ===========================

st.set_page_config(
    page_title="RAG Chat Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        /* Global background and text colors */
        body {
            background-color: #f7f9fc;
            color: #1e1e1e;
        }

        /* Main content area */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        /* Chat input area */
        .stChatInput {
            background-color: #ffffff;
            border-radius: 10px;
            border: 1px solid #e6e6e6;
        }

        /* Chat bubbles */
        div[data-testid="stChatMessage"] {
            border-radius: 10px;
            padding: 0.75rem 1rem;
            margin-bottom: 0.5rem;
        }

        div[data-testid="stChatMessage-user"] {
            background-color: #dceffd;
            text-align: right;
        }

        div[data-testid="stChatMessage-assistant"] {
            background-color: #f3f2ff;
        }

        /* Titles */
        h1 {
            color: #3c3cfa;
            text-align: center;
            font-weight: 800;
        }

        /* File uploader */
        section[data-testid="stFileUploader"] {
            background-color: #ffffff;
            border: 1px dashed #3c3cfa;
            border-radius: 10px;
            padding: 20px;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #262730;
            color: white !important;
        }

        [data-testid="stSidebar"] h2 {
            color: #f8f9fa !important;
        }

        /* Buttons */
        .stButton button {
            background: linear-gradient(90deg, #3c3cfa, #7a68ff);
            color: white;
            border-radius: 6px;
            border: none;
        }

        .stButton button:hover {
            background: linear-gradient(90deg, #6b5cff, #3c3cfa);
        }
    </style>
""", unsafe_allow_html=True)

# ===========================
# ⚙️ Backend URL
# ===========================
BACKEND_URL = "https://rag-backend-961057228920.us-central1.run.app"

# ===========================
# 🧠 Session Management
# ===========================
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

# ===========================
# 🧍 Sidebar (User Info)
# ===========================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/robot-2.png", width=80)
    st.markdown("## 👋 Welcome to RAG Chat Assistant")
    username = st.text_input("Enter your name:", value="Guest")
    st.caption(f"💬 **Session ID:** `{st.session_state.session_id[:8]}`")
    if st.button("🔄 Start New Session"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.experimental_rerun()
    st.markdown("---")
    st.markdown("**Powered by FastAPI + Azure OpenAI + Streamlit**")
    st.caption("Deployed on Google Cloud Run ☁️")

# ===========================
# 🏠 Main Layout
# ===========================
st.title("🤖 RAG AI Chat Assistant")
st.markdown("""
Chat intelligently with your uploaded documents.<br>
Upload a **PDF**, ask a **question**, and let the AI answer based on its contents.
""", unsafe_allow_html=True)

st.divider()

# ===========================
# 📄 File Upload Section
# ===========================
uploaded_files = st.file_uploader(
    "📁 Upload one or more PDFs to analyze",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    with st.spinner("📤 Uploading and processing files..."):
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

st.divider()

# ===========================
# 💬 Chat Section
# ===========================
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

if prompt := st.chat_input("💬 Ask something about your uploaded PDFs..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)

    with st.chat_message("assistant"):
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
                        source_text = "\n\n**📚 Sources:**\n" + "\n".join(
                            [f"- {s.get('filename', '')}" for s in sources]
                        )
                        answer += source_text
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error(f"❌ API error: {res.text}")
            except Exception as e:
                st.error(f"🚨 Error: {e}")
