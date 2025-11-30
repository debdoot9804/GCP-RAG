import streamlit as st
import requests
import uuid

# 🔗 Backend API
BACKEND_URL = "https://rag-backend-961057228920.us-central1.run.app"

# 🎯 Page Setup
st.set_page_config(page_title="RAG Chatbot", page_icon="🤖", layout="wide")
st.title("🤖 RAG AI Chat Assistant")
st.markdown("Chat with your uploaded documents — powered by **FastAPI + Azure OpenAI**")

# 🧠 Persistent Session ID
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# 📤 File Upload Section
uploaded_files = st.file_uploader("Upload one or more PDFs", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    with st.spinner("Processing your PDFs..."):
        try:
            files = [("files", (f.name, f, "application/pdf")) for f in uploaded_files]
            res = requests.post(
                f"{BACKEND_URL}/upload/",
                params={"session_id": st.session_state.session_id},
                files=files,
                timeout=300
            )
            if res.status_code == 200:
                st.success("✅ Files processed successfully!")
            else:
                st.error(f"❌ Upload failed: {res.text}")
        except Exception as e:
            st.error(f"🚨 Upload error: {e}")

st.divider()

# 💬 Chat UI
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    role, content = msg["role"], msg["content"]
    st.chat_message(role).markdown(content)

if prompt := st.chat_input("Ask something about your PDFs..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
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
