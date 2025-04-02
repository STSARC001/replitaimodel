import os
import time
import google.generativeai as genai
from typing import Tuple, List

# Configure the Gemini API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

genai.configure(api_key=GEMINI_API_KEY)

def generate_story(prompt: str) -> Tuple[str, str]:
    """
    Generate a story using the Gemini API based on the provided prompt.
    
    Args:
        prompt (str): The story prompt describing the type, theme, and other parameters
        
    Returns:
        Tuple[str, str]: The story title and the story text
    """
    try:
        # Create a more detailed prompt for the Gemini model
        detailed_prompt = f"""
        You are a creative storyteller.
        
        {prompt}
        
        Create an engaging and descriptive story with the following:
        1. A clear beginning, middle, and end
        2. Vivid descriptions of settings and characters
        3. Dialogue where appropriate
        4. Emotional moments
        5. A satisfying ending
        
        The story should be divided into clear scenes or sections, with good pacing.
        
        First, provide a title for the story on the first line, preceded by "TITLE: "
        Then, provide the complete story text.
        """
        
        # Generate content using Gemini
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(detailed_prompt)
        
        # Process the response to extract title and story
        response_text = response.text
        lines = response_text.split('\n')
        
        # Extract title (assuming it's on the first line or marked with TITLE:)
        title = "Untitled Story"
        story_text = response_text
        
        for line in lines:
            if line.startswith("TITLE:"):
                title = line.replace("TITLE:", "").strip()
                story_text = response_text.replace(line, "").strip()
                break
            elif "title:" in line.lower():
                title = line.lower().replace("title:", "").strip()
                story_text = response_text.replace(line, "").strip()
                break
        
        # Fallback in case no title was found - take first line
        if title == "Untitled Story" and len(lines) > 0:
            title = lines[0].strip()
            story_text = '\n'.join(lines[1:]).strip()
        
        return title, story_text
        
    except Exception as e:
        print(f"Error in generate_story: {e}")
        return "Error in Story Generation", f"We encountered an error: {str(e)}\nPlease try again."

def generate_story_image_prompts(story_text: str, style: str = "Cartoon") -> List[str]:
    """
    Generate image prompts for different scenes in the story.
    
    Args:
        story_text (str): The full story text
        style (str): The visual style for the images (e.g., Cartoon, Realistic)
        
    Returns:
        List[str]: List of image prompts for each scene
    """
    try:
        # Create a prompt for Gemini to extract key scenes
        extract_prompt = f"""
        From the following story, identify 3-5 key visual scenes that would make 
        compelling images or short video clips. For each scene, write a detailed 
        description that could be used as a prompt for image or video generation.
        
        The visual style should be: {style}
        
        Each prompt should be clear, descriptive, and capture a key moment from the story.
        Include details about characters, setting, action, mood, lighting, and perspective.
        
        Format your response as a list, with each scene description on a separate line 
        starting with "SCENE: ".
        
        Here's the story:
        
        {story_text}
        """
        
        # Generate scene descriptions using Gemini
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(extract_prompt)
        
        # Process the response to extract scene descriptions
        scene_prompts = []
        lines = response.text.split('\n')
        
        current_scene = ""
        for line in lines:
            if line.strip().startswith("SCENE:"):
                if current_scene:
                    scene_prompts.append(current_scene.strip())
                current_scene = line.replace("SCENE:", "").strip()
            elif "scene:" in line.lower() and not current_scene:
                current_scene = line.lower().replace("scene:", "").strip()
            elif current_scene:
                current_scene += " " + line.strip()
        
        # Add the last scene if it exists
        if current_scene:
            scene_prompts.append(current_scene.strip())
        
        # If no scenes were identified, create at least one general prompt
        if not scene_prompts:
            general_prompt = f"A {style.lower()} style illustration depicting a key moment from the story: {story_text[:200]}..."
            scene_prompts.append(general_prompt)
        
        # Enhance each prompt with the style specification
        enhanced_prompts = []
        for i, prompt in enumerate(scene_prompts):
            if style.lower() not in prompt.lower():
                enhanced_prompt = f"{prompt} Style: {style}, high quality, detailed."
            else:
                enhanced_prompt = f"{prompt}, high quality, detailed."
            enhanced_prompts.append(enhanced_prompt)
        
        return enhanced_prompts
        
    except Exception as e:
        print(f"Error in generate_story_image_prompts: {e}")
        return [f"Error generating image prompts: {str(e)}"]
