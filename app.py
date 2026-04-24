import streamlit as st
import os
import tempfile
import asyncio
from moviepy import ImageClip, AudioFileClip
import edge_tts

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="Cartoon Video Software - GlobalInternet.py",
    page_icon="🎬",
    layout="centered"
)

# ========== SESSION STATE ==========
if "video_path" not in st.session_state:
    st.session_state.video_path = None

# ========== SIDEBAR INFO ==========
st.sidebar.image("https://img.icons8.com/color/96/null/video-call--v1.png", width=80)
st.sidebar.markdown("### 🎬 Cartoon Video Software")
st.sidebar.markdown("**Built by Gesner Deslandes**")
st.sidebar.markdown("📞 (509) 4738-5663")
st.sidebar.markdown("✉️ deslandes78@gmail.com")
st.sidebar.markdown("🌐 [GlobalInternet.py](https://globalinternetsitepy-abh7v6tnmskxxnuplrdcgk.streamlit.app/)")
st.sidebar.markdown("---")
st.sidebar.markdown("**How it works:**")
st.sidebar.markdown("1️⃣ Upload a cartoon character image (man in suit, sitting at desk).")
st.sidebar.markdown("2️⃣ Write or paste a script.")
st.sidebar.markdown("3️⃣ Generate AI voice (male, calm).")
st.sidebar.markdown("4️⃣ Download video with image + audio.")

st.title("🎬 Cartoon Video Software")
st.markdown("Create a professional talking‑head video of a **black man in a suit** introducing **GlobalInternet.py**.")

default_script = """Hello, I'm the face of GlobalInternet.py. We build custom Python software, AI solutions, election systems, business dashboards, educational books, employee management software, hospital systems, and much more. From Haiti to the world – let’s build your project together. Visit our website today."""

with st.form("video_form"):
    uploaded_image = st.file_uploader("📸 Upload cartoon character image (black man in suit, sitting at desk)", type=["png", "jpg", "jpeg"])
    script = st.text_area("📝 Script (what the character will say)", value=default_script, height=150)
    voice_options = {
        "Guy (English US)": "en-US-GuyNeural",
        "Davis (English US)": "en-US-DavisNeural",
        "Christopher (English US)": "en-US-ChristopherNeural"
    }
    selected_voice = st.selectbox("🎙️ AI Voice", list(voice_options.keys()))
    voice_id = voice_options[selected_voice]
    generate = st.form_submit_button("🎬 Generate Video")

async def text_to_speech(text, voice, output_file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

if generate:
    if not uploaded_image:
        st.error("❌ Please upload a cartoon character image.")
    elif not script.strip():
        st.error("❌ Please write a script.")
    else:
        with st.spinner("🖼️ Processing image..."):
            # Save uploaded image to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
                tmp_img.write(uploaded_image.getvalue())
                image_path = tmp_img.name
        
        with st.spinner("🎤 Generating AI voice..."):
            # Save audio to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
                audio_path = tmp_audio.name
            asyncio.run(text_to_speech(script, voice_id, audio_path))
        st.success("✅ Voice generated!")
        
        with st.spinner("🎬 Creating video... this may take up to 30 seconds"):
            # Load audio
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            
            # Create image clip with same duration as audio
            img_clip = ImageClip(image_path).resized(height=720).with_duration(duration).with_audio(audio_clip)
            
            # Write video to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_video:
                video_path = tmp_video.name
            img_clip.write_videofile(video_path, fps=24, codec='libx264', audio_codec='aac', logger=None)
            
            # Clean up temp files
            os.unlink(audio_path)
            os.unlink(image_path)
            
            st.session_state.video_path = video_path
            st.success("🎉 Video created successfully!")
            
            # Display video
            st.video(video_path)
            
            # Download button
            with open(video_path, "rb") as f:
                st.download_button("📥 Download Video", f, file_name="globalinternet_promo.mp4", mime="video/mp4")

st.markdown("---")
st.caption("⚡ Powered by edge-tts (Microsoft Neural Voices) and MoviePy. Built by Gesner Deslandes for GlobalInternet.py.")
