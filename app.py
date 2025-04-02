import os
import time
import streamlit as st
import torch
from PIL import Image
import base64
import tempfile

from gemini_generator import generate_story, generate_story_image_prompts
from bark_generator import generate_audio
from opensora_generator import generate_video
from video_compiler import compile_final_video
from utils import create_progress_bar, save_text_to_file

# Page configuration
st.set_page_config(
    page_title="AI Story Creator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("AI Story Creator")
st.markdown("""
Generate animated stories with AI-powered visuals and narration.
This app uses Gemini for story generation, OpenSora for video creation,
and Bark AI for voice narration.
""")

# Sidebar for controls and parameters
st.sidebar.header("Story Parameters")

# Story theme selection
story_theme = st.sidebar.selectbox(
    "Story Theme",
    ["Adventure", "Fantasy", "Science Fiction", "Mystery", "Fairy Tale", "Fable", "Educational", "Custom"],
    index=0
)

# Target audience
target_audience = st.sidebar.selectbox(
    "Target Audience",
    ["Children (3-8)", "Pre-teens (9-12)", "Teenagers", "Adults", "All Ages"],
    index=4
)

# Story length
story_length = st.sidebar.select_slider(
    "Story Length",
    options=["Very Short", "Short", "Medium", "Long"],
    value="Short"
)

# Custom theme input if selected
custom_theme = ""
if story_theme == "Custom":
    custom_theme = st.sidebar.text_input("Enter Custom Theme")

# Character settings
st.sidebar.header("Character Settings")
main_character = st.sidebar.text_input("Main Character Name/Type (optional)")
character_traits = st.sidebar.text_input("Character Traits (optional, comma-separated)")

# Video settings
st.sidebar.header("Video Settings")
video_style = st.sidebar.selectbox(
    "Video Style",
    ["Realistic", "Cartoon", "Anime", "Watercolor", "3D Animation"],
    index=1
)

# Audio settings
st.sidebar.header("Audio Settings")
narrator_voice = st.sidebar.selectbox(
    "Narrator Voice",
    ["Male", "Female", "Child"],
    index=0
)

# Process Button
generate_btn = st.sidebar.button("Generate Story", type="primary")

# Initialize session state for storing results
if 'story_text' not in st.session_state:
    st.session_state.story_text = None
if 'story_title' not in st.session_state:
    st.session_state.story_title = None
if 'image_prompts' not in st.session_state:
    st.session_state.image_prompts = []
if 'audio_file' not in st.session_state:
    st.session_state.audio_file = None
if 'video_file' not in st.session_state:
    st.session_state.video_file = None
if 'final_video' not in st.session_state:
    st.session_state.final_video = None
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'current_step' not in st.session_state:
    st.session_state.current_step = None

# Main content area with tabs
tab1, tab2, tab3, tab4 = st.tabs(["Story Generation", "Voice Narration", "Video Creation", "Final Result"])

# Helper function to check CUDA availability
def check_resources():
    if not torch.cuda.is_available():
        st.warning("CUDA is not available. Video and audio generation may be slow or fail. Consider using a GPU-enabled runtime.")
        return False
    return True

# Process the story generation pipeline
if generate_btn and not st.session_state.processing:
    if check_resources():
        st.session_state.processing = True
        st.session_state.current_step = "story_generation"
        
        # Construct story prompt
        story_prompt = f"Create a {story_length.lower()} {story_theme.lower() if story_theme != 'Custom' else custom_theme} story for {target_audience.lower()} audience"
        
        if main_character:
            story_prompt += f" featuring {main_character}"
            if character_traits:
                story_prompt += f" who is {character_traits}"
        
        with tab1:
            with st.spinner("Generating story..."):
                progress_bar = create_progress_bar(0, "Generating story")
                
                # Generate the story
                st.session_state.story_title, st.session_state.story_text = generate_story(story_prompt)
                progress_bar.progress(50, text="Generating image prompts")
                
                # Generate image prompts for each scene
                st.session_state.image_prompts = generate_story_image_prompts(
                    st.session_state.story_text, 
                    video_style
                )
                progress_bar.progress(100, text="Story generated")
                
                # Display the story
                st.subheader(st.session_state.story_title)
                st.write(st.session_state.story_text)
                
                # Display image prompts
                st.subheader("Scene Descriptions")
                for i, prompt in enumerate(st.session_state.image_prompts):
                    st.write(f"**Scene {i+1}**: {prompt}")
                
                # Save story text for audio generation
                story_text_file = save_text_to_file(st.session_state.story_text)
        
        # Move to voice narration step
        st.session_state.current_step = "voice_narration"
        
        # Switch to the voice narration tab
        tab2.get_active = True
        time.sleep(1)  # Small delay to ensure UI updates
        
        with tab2:
            with st.spinner("Generating voice narration..."):
                progress_bar = create_progress_bar(0, "Processing text for narration")
                
                # Generate audio from the story text
                progress_bar.progress(30, text="Generating audio narration")
                st.session_state.audio_file = generate_audio(st.session_state.story_text, narrator_voice)
                progress_bar.progress(100, text="Voice narration complete")
                
                # Display audio
                st.audio(st.session_state.audio_file)
        
        # Move to video generation step
        st.session_state.current_step = "video_generation"
        
        # Switch to video creation tab
        tab3.get_active = True
        time.sleep(1)  # Small delay to ensure UI updates
        
        with tab3:
            with st.spinner("Generating video scenes..."):
                progress_bar = create_progress_bar(0, "Setting up video generation")
                
                # Generate video from image prompts
                video_files = []
                for i, prompt in enumerate(st.session_state.image_prompts):
                    progress_percent = int((i / len(st.session_state.image_prompts)) * 80)
                    progress_bar.progress(progress_percent, text=f"Generating scene {i+1}/{len(st.session_state.image_prompts)}")
                    
                    video_file = generate_video(prompt, video_style)
                    video_files.append(video_file)
                    
                    # Display the generated video
                    st.video(video_file)
                
                progress_bar.progress(90, text="Compiling video scenes")
                
                # Combine all videos into one
                st.session_state.video_file = video_files
                progress_bar.progress(100, text="Video creation complete")
        
        # Move to final compilation step
        st.session_state.current_step = "final_compilation"
        
        # Switch to final result tab
        tab4.get_active = True
        time.sleep(1)  # Small delay to ensure UI updates
        
        with tab4:
            with st.spinner("Compiling final video with narration..."):
                progress_bar = create_progress_bar(0, "Starting final compilation")
                
                # Compile final video with audio narration
                progress_bar.progress(30, text="Merging video and audio")
                st.session_state.final_video = compile_final_video(
                    st.session_state.video_file, 
                    st.session_state.audio_file,
                    st.session_state.story_title
                )
                progress_bar.progress(100, text="Final video compilation complete")
                
                # Display final video
                st.subheader(f"Final Story: {st.session_state.story_title}")
                st.video(st.session_state.final_video)
                
                # Download button for final video
                with open(st.session_state.final_video, "rb") as file:
                    video_bytes = file.read()
                    
                st.download_button(
                    label="Download Video",
                    data=video_bytes,
                    file_name=f"{st.session_state.story_title.replace(' ', '_')}.mp4",
                    mime="video/mp4"
                )
        
        st.session_state.processing = False
        st.balloons()
        
# Display existing results if available
if not st.session_state.processing:
    # Story tab
    with tab1:
        if st.session_state.story_text:
            st.subheader(st.session_state.story_title)
            st.write(st.session_state.story_text)
            
            if st.session_state.image_prompts:
                st.subheader("Scene Descriptions")
                for i, prompt in enumerate(st.session_state.image_prompts):
                    st.write(f"**Scene {i+1}**: {prompt}")
    
    # Audio tab
    with tab2:
        if st.session_state.audio_file:
            st.subheader("Story Narration")
            st.audio(st.session_state.audio_file)
    
    # Video tab
    with tab3:
        if st.session_state.video_file:
            st.subheader("Generated Video Scenes")
            for i, video in enumerate(st.session_state.video_file):
                st.write(f"Scene {i+1}")
                st.video(video)
    
    # Final video tab
    with tab4:
        if st.session_state.final_video:
            st.subheader(f"Final Story: {st.session_state.story_title}")
            st.video(st.session_state.final_video)
            
            # Download button for final video
            with open(st.session_state.final_video, "rb") as file:
                video_bytes = file.read()
                
            st.download_button(
                label="Download Video",
                data=video_bytes,
                file_name=f"{st.session_state.story_title.replace(' ', '_')}.mp4",
                mime="video/mp4"
            )

# Show current processing step
if st.session_state.processing:
    if st.session_state.current_step == "story_generation":
        st.info("Generating story... Please wait.")
    elif st.session_state.current_step == "voice_narration":
        st.info("Generating voice narration... Please wait.")
    elif st.session_state.current_step == "video_generation":
        st.info("Generating video scenes... Please wait.")
    elif st.session_state.current_step == "final_compilation":
        st.info("Compiling final video... Please wait.")
