import streamlit as st
import os
import time
import tempfile
import speech_recognition as sr
from gtts import gTTS
from dotenv import load_dotenv

# Handle Git path issues on Windows
git_path = r"C:\Program Files\Git\bin\git.exe"
if not os.path.exists(git_path):
    git_path = r"C:\Program Files\Git\cmd\git\git.exe" 
if not os.path.exists(git_path):
    git_path = r"C:\Users\Yeagerist\AppData\Local\Programs\Git\bin\git.exe"

if os.path.exists(git_path):
    os.environ["GIT_PYTHON_GIT_EXECUTABLE"] = git_path

# Imports
from ingestion import ingest_repo
from db import list_collections
from chat_manager import save_chat_history, load_chat_history

# Module 3 Imports
from reasoning_core import agent
from network import measure_latency, get_network_mode
from native_rag import native_db, manual_chunk_text
import pdfplumber

# Auth Import
import auth

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="Adaptive AI Agent",
    page_icon="🧠",
    layout="wide"
)

# --- AUDIO HELPERS ---
def transcribe_audio(audio_bytes):
    r = sr.Recognizer()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        tmp_file.write(audio_bytes)
        tmp_file.flush()
        with sr.AudioFile(tmp_file.name) as source:
            audio = r.record(source)
    try:
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Sorry, I could not understand the audio."
    except sr.RequestError as e:
        return f"Could not request results; {e}"

def text_to_speech(text):
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
            tts = gTTS(text=text, lang='en')
            tts.save(tmp_file.name)
            return tmp_file.name
    except Exception as e:
        st.error(f"TTS Error: {e}")
        return None

# --- MAIN APP ---

if auth.login():
    st.title("🧠 Adaptive Reasoning Agent")
    user = auth.get_current_user()

    # Sidebar
    with st.sidebar:
        st.write(f"Logged in as: **{user}**")
        if st.button("Logout"):
            auth.logout()
        
        st.divider()
        st.header("Status & Context")
        
        # --- Network Sensor ---
        if st.button("📡 Check Network Latency"):
            latency = measure_latency()
            mode = get_network_mode(latency)
            st.session_state.network_mode = mode
            st.session_state.latency = latency
            start_msg = f"Latency: {latency:.0f}ms -> **{mode} MODE**"
            if mode == "DEEP":
                st.success(start_msg)
            elif mode == "STANDARD":
                st.warning(start_msg)
            else:
                st.error(start_msg)
        
        st.caption(f"Current Mode: **{st.session_state.get('network_mode', 'UNKNOWN')}**")
        st.divider()

        # --- History List ---
        st.subheader("Your Chats (Repositories)")
        collections = list_collections()
        
        if st.button("+ New Chat / Add Repo", use_container_width=True):
            st.session_state.current_collection = None
            st.session_state.messages = []
            st.rerun()

        if collections:
            index = 0
            if st.session_state.get("current_collection") in collections:
                index = collections.index(st.session_state["current_collection"])
            
            selected_collection = st.radio(
                "Select a Repository Context:",
                collections,
                index=index,
                key="repo_list",
                label_visibility="collapsed"
            )
            
            if selected_collection and selected_collection != st.session_state.get("last_loaded_collection"):
                st.session_state.current_collection = selected_collection
                st.session_state.messages = load_chat_history(user, selected_collection)
                st.session_state.last_loaded_collection = selected_collection
                st.rerun()
        else:
            st.info("No repository chats yet.")

        st.divider()

        # --- Ingest New Repo ---
        with st.expander("Add New Repository", expanded=(st.session_state.get("current_collection") is None)):
            new_repo_url = st.text_input("GitHub Repo URL", placeholder="https://github.com/owner/repo")
            mistral_api_key = st.text_input("Mistral API Key", type="password", value=os.getenv("MISTRAL_API_KEY", ""))
            
            if st.button("Ingest New Repo"):
                if not new_repo_url:
                    st.error("Enter a URL")
                else:
                    with st.spinner("Processing & Vectorizing..."):
                        try:
                            result = ingest_repo(new_repo_url)
                            if result.get("status") == "success":
                                st.success(result["message"])
                                st.session_state.current_collection = result["collection_name"]
                                st.session_state.messages = [] 
                                save_chat_history(user, result["collection_name"], [])
                                st.rerun()
                            else:
                                st.error(result.get("message"))
                        except Exception as e:
                            st.error(f"Error: {e}")

        st.divider()
        
         # --- Native RAG ---
        st.subheader("Document Context (Native)")
        uploaded_files = st.file_uploader("Upload PDF/Text", accept_multiple_files=True)
        if uploaded_files:
            if st.button("Process Documents"):
                with st.spinner("Chunking..."):
                    all_texts = []
                    for file in uploaded_files:
                        try:
                            text = ""
                            if file.name.endswith(".pdf"):
                                with pdfplumber.open(file) as pdf:
                                    for page in pdf.pages:
                                        text += page.extract_text() or ""
                            else:
                                text = file.read().decode("utf-8")
                            
                            chunks = manual_chunk_text(text)
                            all_texts.extend(chunks)
                        except Exception as e:
                            st.error(f"Error {file.name}: {e}")
                    
                    if all_texts:
                        native_db.add_texts(all_texts)
                        st.success(f"Added {len(all_texts)} chunks.")

        if "current_collection" in st.session_state and st.session_state.current_collection:
            st.info(f"Active Context: {st.session_state.current_collection}")
            # Renamed Sync Button
            if st.button("🔄 Refresh Context"):
                 st.toast(f"Checking for updates in {st.session_state.current_collection}...")
                 st.success("Context Refreshed (Simulated Git Pull)")

    # --- MAIN CHAT AREA ---
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "latency" in message:
                 st.caption(f"⏱️ {message['latency']:.0f}ms | {message['mode']}")
            if "audio" in message:
                st.audio(message["audio"])

    # ChatGPT-like Input Area (Text + Voice integrated)
    voice_prompt = None
    
    # Create a container for chat input and voice button
    col1, col2 = st.columns([0.92, 0.08])
    
    with col1:
        prompt = st.chat_input("Ask a question...")
    
    with col2:
        # Voice popover button (like ChatGPT's microphone icon)
        with st.popover("🎙️"):
            st.write("**Voice Input**")
            audio_input = st.audio_input("Record your message", label_visibility="collapsed")
            if audio_input:
                with st.spinner("Transcribing..."):
                    audio_bytes = audio_input.read()
                    voice_prompt = transcribe_audio(audio_bytes)
                    if voice_prompt:
                        st.success(f"Transcribed: {voice_prompt[:50]}...")
                        st.session_state.voice_prompt = voice_prompt
    
    # Get voice prompt from session state if it was just set
    if "voice_prompt" in st.session_state and st.session_state.voice_prompt:
        voice_prompt = st.session_state.voice_prompt
        st.session_state.voice_prompt = None  # Clear it
    
    # Combined Prompt
    final_prompt = prompt or voice_prompt

    if final_prompt:
        st.session_state.messages.append({"role": "user", "content": final_prompt})
        
        if "current_collection" in st.session_state and st.session_state.current_collection:
            save_chat_history(user, st.session_state.current_collection, st.session_state.messages)
            
        with st.chat_message("user"):
            st.markdown(final_prompt)

        with st.chat_message("assistant"):
            if not os.getenv("MISTRAL_API_KEY"):
                 st.error("API Key Missing")
            else:
                with st.spinner("Thinking..."):
                    try:
                        repo_context = st.session_state.get("current_collection", "None")
                        
                        # Streaming response
                        response_stream_gen, mode, latency = agent.run(final_prompt, context=f"Context: {repo_context}", stream=True)
                        
                        # Use streamlit's write_stream
                        response_text = st.write_stream(response_stream_gen)
                        
                        st.caption(f"⏱️ {latency:.0f}ms | {mode}")
                        
                        # Generate Audio ONLY if toggle is on
                        enable_voice = st.session_state.get("enable_voice_response", False)
                        
                        audio_file = None
                        if enable_voice:
                             with st.spinner("Speaking..."):
                                audio_file = text_to_speech(response_text)
                                if audio_file:
                                    st.audio(audio_file, autoplay=True)

                        msg_data = {
                            "role": "assistant", 
                            "content": response_text,
                            "mode": mode,
                            "latency": latency
                        }
                        if audio_file:
                            msg_data["audio"] = audio_file
                            
                        st.session_state.messages.append(msg_data)
                        
                        if "current_collection" in st.session_state and st.session_state.current_collection:
                            save_chat_history(user, st.session_state.current_collection, st.session_state.messages)

                    except Exception as e:
                        st.error(f"Error: {e}")
