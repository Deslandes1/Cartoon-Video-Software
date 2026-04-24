import streamlit as st
import os
import tempfile
import asyncio
from moviepy import ImageClip, AudioFileClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
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
st.sidebar.markdown("4️⃣ Download video with image + audio + subtitles.")

# ========== MAIN INTERFACE ==========
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
    add_subtitles = st.checkbox("✅ Add subtitles (burned into video)", value=True)
    generate = st.form_submit_button("🎬 Generate Video")

async def text_to_speech(text, voice, output_file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

def create_subtitle_image(text, width, height, font_size=28):
    """Create a PIL image with wrapped text for subtitles."""
    # Use a default font (no external file needed, PIL will use default)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Wrap text to fit width
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + " " + word if current_line else word
        # Approximate width (very rough)
        if len(test_line) * (font_size * 0.6) < width - 40:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    
    # Calculate image height
    line_height = font_size + 10
    img_height = len(lines) * line_height + 20
    img = Image.new('RGBA', (width, img_height), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    y = 10
    for line in lines:
        # Center text horizontally
        bbox = draw.textbbox((0,0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y), line, fill=(255,255,255,255), font=font, stroke_width=1, stroke_fill=(0,0,0,255))
        y += line_height
    return img

if generate:
    if not uploaded_image:
        st.error("❌ Please upload a cartoon character image.")
    elif not script.strip():
        st.error("❌ Please write a script.")
    else:
        # Save image
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
            tmp_img.write(uploaded_image.getvalue())
            image_path = tmp_img.name
        
        # Generate audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
            audio_path = tmp_audio.name
        with st.spinner("🎤 Generating AI voice..."):
            asyncio.run(text_to_speech(script, voice_id, audio_path))
        st.success("✅ Voice generated!")
        
        # Create video
        with st.spinner("🎬 Creating video (this may take a moment)..."):
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            
            # Image clip
            img_clip = ImageClip(image_path).resized(height=720).with_duration(duration).with_audio(audio_clip)
            
            if add_subtitles:
                # Get dimensions of the image clip
                img_width = img_clip.w
                img_height = img_clip.h
                # Create subtitle PIL image
                subtitle_img = create_subtitle_image(script, img_width, img_height, font_size=24)
                # Save to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_sub:
                    subtitle_img.save(tmp_sub.name, format="PNG")
                    subtitle_path = tmp_sub.name
                # Create ImageClip for subtitle
                sub_clip = ImageClip(subtitle_path).with_duration(duration)
                # Position at bottom
                sub_clip = sub_clip.with_position(('center', img_height - sub_clip.h - 20))
                final_clip = CompositeVideoClip([img_clip, sub_clip])
                os.unlink(subtitle_path)
            else:
                final_clip = img_clip
            
            # Write video
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_video:
                video_path = tmp_video.name
            final_clip.write_videofile(video_path, fps=24, codec='libx264', audio_codec='aac', logger=None, threads=2)
            
            # Cleanup
            os.unlink(audio_path)
            os.unlink(image_path)
            
            st.session_state.video_path = video_path
            st.success("🎉 Video created successfully!")
            
            # Display and download
            st.video(video_path)
            with open(video_path, "rb") as f:
                st.download_button("📥 Download Video", f, file_name="globalinternet_promo.mp4", mime="video/mp4")

st.markdown("---")
st.caption("⚡ Powered by edge-tts and MoviePy. Built by Gesner Deslandes for GlobalInternet.py.")
