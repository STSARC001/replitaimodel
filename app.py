import os
import time
import streamlit as st
import tempfile
from PIL import Image
import base64

from gemini_generator import generate_story, generate_story_image_prompts
from gemini_image_generator import generate_scene_images
from utils import create_progress_bar, save_text_to_file, check_api_keys

# Page configuration
st.set_page_config(
    page_title="AI Story Creator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Check for API keys before proceeding
if not check_api_keys():
    st.error("Please set the GEMINI_API_KEY environment variable to use this application.")
    st.info("You can add your API key by clicking on the 'Secrets' tab in the Replit sidebar.")
    st.stop()

# Title and description
st.title("Automatic AI Story Creator")
st.markdown("""
### 🔮 Simply select a theme to instantly generate a story!
The app will automatically create a complete story with illustrated scenes as soon as you choose a theme. No buttons to press!
""")

# Simplified sidebar for theme selection only
st.sidebar.header("Story Theme")

# Story theme selection - using a key to detect changes
story_theme = st.sidebar.selectbox(
    "Select a Theme to Generate Story",
    ["Adventure", "Fantasy", "Science Fiction", "Mystery", "Fairy Tale", "Fable", "Educational", "Superhero", "Space Exploration", "Underwater Adventure", "Time Travel", "Historical", "Animal Friends", "Magical Creatures", "Custom"],
    index=0,
    key="theme_selector"
)

# Custom theme input if selected
custom_theme = ""
if story_theme == "Custom":
    custom_theme = st.sidebar.text_input("Enter Custom Theme", key="custom_theme_input")

# Auto-set default values for other parameters
target_audience = "All Ages"
story_length = "Medium"
main_character = ""
character_traits = ""
image_style = "Cartoon"
num_scenes = 3

# Add information about automatic generation
st.sidebar.markdown("---")
st.sidebar.info("👆 Story will generate automatically when you select a theme!")

# Track theme changes to auto-generate content
if 'last_theme' not in st.session_state:
    st.session_state.last_theme = None
    
if 'last_custom_theme' not in st.session_state:
    st.session_state.last_custom_theme = None

# Set generate flag based on theme changes
generate_story_now = False

# Check if theme has changed
if st.session_state.last_theme != story_theme:
    st.session_state.last_theme = story_theme
    generate_story_now = True
    
# For custom theme, also check if custom theme text changed
if story_theme == "Custom" and st.session_state.last_custom_theme != custom_theme:
    st.session_state.last_custom_theme = custom_theme
    generate_story_now = True

# Initialize session state for storing results
if 'story_text' not in st.session_state:
    st.session_state.story_text = None
if 'story_title' not in st.session_state:
    st.session_state.story_title = None
if 'image_prompts' not in st.session_state:
    st.session_state.image_prompts = []
if 'generated_images' not in st.session_state:
    st.session_state.generated_images = []
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'current_step' not in st.session_state:
    st.session_state.current_step = None

# Main content area with tabs
tab1, tab2 = st.tabs(["Story Generation", "Scene Visualization"])

# Process the story generation pipeline
if generate_story_now and not st.session_state.processing:
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
            
            # Generate image prompts for each scene (limit by num_scenes)
            st.session_state.image_prompts = generate_story_image_prompts(
                st.session_state.story_text, 
                image_style
            )[:num_scenes]  # Limit number of scenes
            
            progress_bar.progress(100, text="Story generated")
            
            # Display the story
            st.subheader(st.session_state.story_title)
            st.write(st.session_state.story_text)
            
            # Display image prompts
            st.subheader("Scene Descriptions")
            for i, prompt in enumerate(st.session_state.image_prompts):
                st.write(f"**Scene {i+1}**: {prompt}")
    
    # Move to image generation step
    st.session_state.current_step = "image_generation"
    
    # Switch to the scene visualization tab
    tab2.get_active = True
    time.sleep(1)  # Small delay to ensure UI updates
    
    with tab2:
        with st.spinner("Generating scene images..."):
            progress_bar = create_progress_bar(0, "Setting up image generation")
            
            # Generate images for each scene
            st.session_state.generated_images = []
            for i, prompt in enumerate(st.session_state.image_prompts):
                progress_percent = int((i / len(st.session_state.image_prompts)) * 90)
                progress_bar.progress(progress_percent, text=f"Generating image {i+1}/{len(st.session_state.image_prompts)}")
                
                # Generate image for the scene
                image_path = generate_scene_images([prompt], image_style)[0]
                st.session_state.generated_images.append(image_path)
                
                # Display the generated image
                st.subheader(f"Scene {i+1}")
                st.image(image_path, caption=prompt[:100] + "..." if len(prompt) > 100 else prompt)
            
            progress_bar.progress(100, text="Image generation complete")
    
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
    
    # Images tab
    with tab2:
        if st.session_state.generated_images:
            st.subheader("Generated Scene Images")
            for i, (image_path, prompt) in enumerate(zip(st.session_state.generated_images, st.session_state.image_prompts)):
                st.subheader(f"Scene {i+1}")
                st.image(image_path, caption=prompt[:100] + "..." if len(prompt) > 100 else prompt)
                
                # Download button for each image
                with open(image_path, "rb") as file:
                    image_bytes = file.read()
                    
                st.download_button(
                    label=f"Download Scene {i+1}",
                    data=image_bytes,
                    file_name=f"scene_{i+1}.png",
                    mime="image/png"
                )

# Show current processing step
if st.session_state.processing:
    if st.session_state.current_step == "story_generation":
        st.info("Generating story... Please wait.")
    elif st.session_state.current_step == "image_generation":
        st.info("Generating scene images... Please wait.")
