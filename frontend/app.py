import streamlit as st
import requests
import uuid

# 🎯 Your FastAPI backend URL
BACKEND_URL = "https://rag-backend-961057228920.us-central1.run.app"

# Page config
st.set_page_config(page_title="RAG Chatbot", page_icon="🤖", layout="wide")

# Session ID (unique per user)
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.title("🤖 RAG AI Chat Assistant")
st.markdown("Chat with your uploaded documents — powered by **FastAPI + Azure OpenAI**")

# File upload
uploaded_file = st.file_uploader("📄 Upload a PDF to index", type=["pdf"])

if uploaded_file:
    with st.spinner("📤 Uploading file..."):
        files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
        try:


            res = requests.post(
    f"{BACKEND_URL}/upload",
    params={"session_id": st.session_state.session_id},
    files={"files": (uploaded_file.name, uploaded_file, "application/pdf")},
)

            #res = requests.post(f"{BACKEND_URL}/upload", files=files)
            if res.status_code == 200:
                st.success(f"✅ {uploaded_file.name} uploaded successfully!")
            else:
                st.error(f"❌ Upload failed: {res.text}")
        except Exception as e:
            st.error(f"🚨 Upload error: {e}")

st.divider()

# Chat area
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    role, content = msg["role"], msg["content"]
    if role == "user":
        st.chat_message("user").markdown(content)
    else:
        st.chat_message("assistant").markdown(content)

# Chat input
if prompt := st.chat_input("💬 Ask your question here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            try:
                res = requests.get(
                    f"{BACKEND_URL}/chat",
                    params={"session_id": st.session_state.session_id, "user_input": prompt},
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
