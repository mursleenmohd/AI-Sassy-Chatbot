import streamlit as st
import requests
import json
import uuid

st.set_page_config(page_title="Simple AI Chatbot", page_icon=" ", layout="centered")
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0b0f19 0%, #111827 100%); color: #f3f4f6; }
    .main .block-container { padding-top: 2rem; padding-bottom: 5rem; max-width: 800px; }
    .header-container {
        text-align: center; padding: 1.5rem; background: rgba(31, 41, 55, 0.4);
        backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px; margin-bottom: 2rem; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    [data-testid="stChatMessage"] {
        background-color: rgba(31, 41, 55, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 14px !important; padding: 14px 18px !important;
        margin-bottom: 14px !important;
    }
    .stChatInputContainer {
        border-radius: 16px !important; border: 1px solid rgba(139, 92, 246, 0.3) !important;
        background-color: #1e293b !important;
    }
    #MainMenu, footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="header-container">
        <h1 style="margin:0; font-size: 2rem; color: #f8fafc; font-weight: 700;">Simple AI Chatbot</h1>
        <p style="margin-top: 6px; color: #94a3b8; font-size: 0.95rem;">You can talk to me and Powered by Gemini 3.6 Flash</p>
    </div>
""", unsafe_allow_html=True)

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "What do you want now? Make it quick, I don't have all day."}
    ]

for message in st.session_state.messages:
    avatar_icon = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar_icon):
        st.markdown(message["content"])

if prompt := st.chat_input("Type your query here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            url = "http://fastapi_backend:8000/chat/stream"
            payload = {
                "session_id": st.session_state.session_id,
                "user_input": prompt
            }
            
            response = requests.post(url, json=payload, stream=True, timeout=60)

            if response.status_code == 200:
                buffer = ""
                for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
                    if chunk:
                        buffer += chunk
                        lines = buffer.split("\n\n")
                        buffer = lines.pop()  # Keep partial data in buffer

                        for line in lines:
                            line = line.strip()
                            if line.startswith("data: "):
                                try:
                                    data_json = json.loads(line[6:])
                                    token = data_json.get("content", "")
                                    full_response += token
                                    message_placeholder.markdown(full_response + "▌")
                                except json.JSONDecodeError:
                                    continue
                
                if full_response.strip():
                    message_placeholder.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                else:
                    message_placeholder.markdown("No response received.")
            else:
                st.error(f"API Error Code: {response.status_code}")

        except requests.exceptions.ConnectionError:
            st.error("Backend offline! Check if Uvicorn is running.")
        except Exception as e:
            st.error(f"Stream Error: {e}")