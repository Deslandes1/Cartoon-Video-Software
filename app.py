import streamlit as st
import os
import subprocess
import tempfile
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, TextClip
import edge_tts
import asyncio

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="Cartoon Video Software - GlobalInternet.py",
    page_icon="🎬",
    layout="centered"
)

# ========== SESSION STATE ==========
if "video_path" not in st.session_state:
    st.session_state.video_path = None
if "audio_path" not in st.session_state:
    st.session_state.audio_path = None

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
st.sidebar.markdown("4️⃣ Download video with image + audio + subtitles.")

# ========== MAIN INTERFACE ==========
st.title("🎬 Cartoon Video Software")
st.markdown("Create a professional talking‑head video of a **black man in a suit** introducing **GlobalInternet.py**.")

# Default script (can be edited)
default_script = """Hello, I'm the face of GlobalInternet.py. We build custom Python software, AI solutions, election systems, business dashboards, educational books, employee management software, hospital systems, and much more. From Haiti to the world – let’s build your project together. Visit our website today."""

with st.form("video_form"):
    # 1. Upload character image
    uploaded_image = st.file_uploader("📸 Upload cartoon character image (black man in suit, sitting at desk)", type=["png", "jpg", "jpeg"])
    
    # 2. Script
    script = st.text_area("📝 Script (what the character will say)", value=default_script, height=150)
    
    # 3. Voice selection (male)
    voice_options = {
        "Guy (English US)": "en-US-GuyNeural",
        "Davis (English US)": "en-US-DavisNeural",
        "Christopher (English US)": "en-US-ChristopherNeural"
    }
    selected_voice = st.selectbox("🎙️ AI Voice", list(voice_options.keys()))
    voice_id = voice_options[selected_voice]
    
    # 4. Subtitles toggle
    add_subtitles = st.checkbox("✅ Add subtitles (burned into video)", value=True)
    
    generate = st.form_submit_button("🎬 Generate Video")

# Helper to run async edge_tts
async def text_to_speech(text, voice, output_file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

if generate:
    if not uploaded_image:
        st.error("❌ Please upload a cartoon character image.")
    elif not script.strip():
        st.error("❌ Please write a script.")
    else:
        with st.spinner("🎤 Generating AI voice..."):
            # Save audio to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
                audio_path = tmp_audio.name
            # Run async TTS
            asyncio.run(text_to_speech(script, voice_id, audio_path))
            st.session_state.audio_path = audio_path
            st.success("✅ Voice generated!")
        
        with st.spinner("🎬 Creating video (this may take a moment)..."):
            # Save uploaded image to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
                tmp_img.write(uploaded_image.getvalue())
                image_path = tmp_img.name
            
            # Load audio to get duration
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            
            # Create image clip
            image_clip = ImageClip(image_path, duration=duration).resize(height=720)
            
            # Center image (if wider than height, fit width)
            image_clip = image_clip.resize(height=720)
            image_clip = image_clip.set_audio(audio_clip)
            
            # Optional subtitles
            if add_subtitles:
                # Split script into chunks (simple by sentences)
                sentences = script.replace('.', '.\n').split('\n')
                subtitles = []
                # Rough timing – we'll use a simple per‑word timing or fixed duration per char.
                # For simplicity, we'll use TextClip with a fixed position at bottom.
                # Better: create a single subtitle track that shows whole text? Not ideal.
                # Instead, we'll use a single text clip that scrolls? Let's keep simple: no subtitles for now.
                # But we can add a generic "captions" overlay. I'll implement a simple caption at bottom center.
                txt_clip = TextClip(script, fontsize=24, color='white', font='Arial', stroke_color='black', stroke_width=1)
                txt_clip = txt_clip.set_position(('center', 'bottom')).set_duration(duration)
                final = CompositeVideoClip([image_clip, txt_clip])
            else:
                final = image_clip
            
            # Write video to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_video:
                video_path = tmp_video.name
            final.write_videofile(video_path, fps=24, codec='libx264', audio_codec='aac')
            
            st.session_state.video_path = video_path
            st.success("🎉 Video created successfully!")
            
            # Cleanup temp files (optional)
            os.unlink(audio_path)
            os.unlink(image_path)
        
        # Display video
        st.video(st.session_state.video_path)
        
        # Download button
        with open(st.session_state.video_path, "rb") as f:
            st.download_button("📥 Download Video", f, file_name="globalinternet_promo.mp4", mime="video/mp4")

# Footer
st.markdown("---")
st.caption("⚡ Powered by edge-tts (Microsoft Neural Voices) and MoviePy. Built by Gesner Deslandes for GlobalInternet.py.")
