import streamlit as st
import os
import tempfile
import asyncio
import replicate
import edge_tts

st.set_page_config(page_title="Cartoon Video Software - GlobalInternet.py", page_icon="🎬", layout="centered")

st.sidebar.image("https://img.icons8.com/color/96/null/video-call--v1.png", width=80)
st.sidebar.markdown("### 🎬 Cartoon Video Software")
st.sidebar.markdown("**Built by Gesner Deslandes**")
st.sidebar.markdown("📞 (509) 4738-5663")
st.sidebar.markdown("✉️ deslandes78@gmail.com")
st.sidebar.markdown("🌐 [GlobalInternet.py](https://globalinternetsitepy-abh7v6tnmskxxnuplrdcgk.streamlit.app/)")
st.sidebar.markdown("---")
st.sidebar.markdown("**How it works**")
st.sidebar.markdown("1. Upload a photo (real or cartoon).")
st.sidebar.markdown("2. Write a script or upload audio.")
st.sidebar.markdown("3. Generate AI voice (male).")
st.sidebar.markdown("4. AI lip‑syncs the photo to the voice.")
st.sidebar.markdown("5. Download the MP4 video.")

st.title("🎬 Cartoon Video Software")
st.markdown("Turn any photo into a talking video – perfect for your **GlobalInternet.py** spokesperson.")

default_script = """Hello, I'm the face of GlobalInternet.py. We build custom Python software, AI solutions, election systems, business dashboards, educational books, employee management software, hospital systems, and much more. From Haiti to the world – let's build your project together. Visit our website today."""

voice_options = {
    "Guy (English US)": "en-US-GuyNeural",
    "Davis (English US)": "en-US-DavisNeural",
    "Christopher (English US)": "en-US-ChristopherNeural"
}

async def tts_async(text, voice, out_file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(out_file)

def tts_sync(text, voice, out_file):
    asyncio.run(tts_async(text, voice, out_file))

def run_replicate_wav2lip(image_path, audio_path, api_token):
    os.environ["REPLICATE_API_TOKEN"] = api_token
    try:
        # Using a stable, public Wav2Lip model (sahil2801/wav2lip)
        output = replicate.run(
            "sahil2801/wav2lip:28a3059e717f1f7c3a4c6b9e5d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e",
            input={
                "face": open(image_path, "rb"),
                "audio": open(audio_path, "rb")
            }
        )
        if isinstance(output, list):
            return output[0]
        return output
    except Exception as e:
        st.error(f"Replicate API error: {e}")
        return None

with st.form("video_form"):
    uploaded_image = st.file_uploader("📸 Upload photo (PNG or JPG)", type=["png", "jpg", "jpeg"])
    script = st.text_area("📝 Script (what the character will say)", value=default_script, height=150)
    use_uploaded_audio = st.checkbox("📁 Use your own audio file instead of script?")
    uploaded_audio = None
    if use_uploaded_audio:
        uploaded_audio = st.file_uploader("🎵 Upload audio (MP3 or WAV)", type=["mp3", "wav"])
    selected_voice = st.selectbox("🎙️ AI Voice (if generating from script)", list(voice_options.keys()))
    generate = st.form_submit_button("🎬 Generate Video", type="primary")

if generate:
    if not uploaded_image:
        st.error("❌ Please upload a photo.")
        st.stop()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
        tmp_img.write(uploaded_image.getvalue())
        image_path = tmp_img.name

    if use_uploaded_audio and uploaded_audio:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
            tmp_audio.write(uploaded_audio.getvalue())
            audio_path = tmp_audio.name
        st.info("🎵 Using your uploaded audio.")
    else:
        if not script.strip():
            st.error("❌ Please write a script or upload audio.")
            st.stop()
        with st.spinner("🎤 Generating AI voice..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
                audio_path = tmp_audio.name
            tts_sync(script, voice_options[selected_voice], audio_path)
        st.success("✅ Voice generated!")

    api_token = st.secrets.get("REPLICATE_API_TOKEN")
    if not api_token:
        st.error("❌ Replicate API token not found. Please add it to your Streamlit secrets.")
        st.stop()

    with st.spinner("🎬 Sending to AI cloud for lip‑syncing (usually 20-60 seconds)..."):
        video_url = run_replicate_wav2lip(image_path, audio_path, api_token)

    try:
        os.unlink(image_path)
        os.unlink(audio_path)
    except:
        pass

    if video_url:
        st.success("🎉 Video ready!")
        st.video(video_url)
        st.markdown(f"[📥 Direct Download Link]({video_url})", unsafe_allow_html=True)
        st.info("Right‑click on the video above and choose 'Save video as...' to download.")
    else:
        st.error("❌ Video generation failed. Check your API token or try again later.")

st.markdown("---")
st.caption("⚡ Powered by Microsoft Edge TTS and Replicate's Wav2Lip. Built by Gesner Deslandes for GlobalInternet.py.")
