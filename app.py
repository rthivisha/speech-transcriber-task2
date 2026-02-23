import streamlit as st
import whisper
from streamlit_mic_recorder import mic_recorder
import tempfile

st.set_page_config(page_title="Speech Recognition App", layout="centered")

# Load model
@st.cache_resource
def load_model():
    return whisper.load_model("tiny")

model = load_model()

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------- CUSTOM CSS -----------
st.markdown("""
<style>

/* Page background */
.stApp {
    background-color: #f4f6fb;
}

/* Main Title */
.title {
    text-align: center;
    font-size: 32px;
    font-weight: bold;
    color: #3b3b98;
}

/* Gradient line under title */
.title::after {
    content: "";
    display: block;
    width: 140px;
    height: 4px;
    margin: 12px auto 25px auto;
    border-radius: 10px;
    background: linear-gradient(90deg, #6a11cb, #2575fc);
}

/* Subtitle */
.subtitle {
    text-align: center;
    font-size: 16px;
    color: #181833;
    margin-bottom: 30px;
}

/* Elegant divider line */
.elegant-divider {
    height: 1px;
    width: 80%;
    margin: 30px auto;
    background: linear-gradient(to right, transparent, #b8c6ff, transparent);
}

/* Chat container */
.chat-container {
    position: relative;
    max-width: 700px;
    margin: auto;
    padding-left: 20px;
}

/* Vertical gradient side accent */
.chat-container::before {
    content: "";
    position: absolute;
    left: 0;
    top: 10px;
    bottom: 10px;
    width: 4px;
    border-radius: 10px;
    background: linear-gradient(to bottom, #6a11cb, #2575fc);
}

/* User bubble */
.user-bubble {
    background: linear-gradient(135deg, #6a11cb, #2575fc);
    color: white;
    padding: 12px 16px;
    border-radius: 20px;
    margin: 10px 0;
    width: fit-content;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

/* Bot bubble */
.bot-bubble {
    background: #dfe4ff;
    padding: 12px 16px;
    border-radius: 20px;
    margin: 10px 0;
    margin-left: auto;
    width: fit-content;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}


/* Subtle animated top line */
.top-glow-line {
    height: 2px;
    width: 60%;
    margin: 20px auto;
    background: linear-gradient(90deg, transparent, #6a11cb, transparent);
    animation: glow 2s infinite alternate;
}

@keyframes glow {
    from { opacity: 0.4; }
    to { opacity: 1; }
}

</style>
""", unsafe_allow_html=True)

# ----------- HEADER -----------
st.markdown('<div class="title">🎧 Speech Recognition App</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Convert your voice into real-time text instantly with AI-powered transcription.</div>', unsafe_allow_html=True)

st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-bubble">{msg["content"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ----------- RECORDER SECTION -----------
st.markdown('<div class="recorder-box">', unsafe_allow_html=True)

audio = mic_recorder(
    start_prompt="🔴 Start Recording",
    stop_prompt="⏹ Stop Recording",
    key="recorder"
)

st.markdown('</div>', unsafe_allow_html=True)

# ----------- TRANSCRIPTION LOGIC -----------

# Store last processed audio id
if "last_audio_id" not in st.session_state:
    st.session_state.last_audio_id = None

if audio:

    current_id = audio["id"]  # unique id from mic_recorder

    # Process only if it's a new recording
    if current_id != st.session_state.last_audio_id:

        st.session_state.last_audio_id = current_id

        with st.spinner("🔄 Transcribing..."):

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio["bytes"])
                tmp_path = tmp_file.name

            result = model.transcribe(tmp_path)
            text = result["text"]

            st.session_state.messages.append(
                {"role": "assistant", "content": text}
            )

        st.rerun()