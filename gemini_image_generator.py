import os
import tempfile
import mimetypes
import base64
from typing import List, Tuple
import google.generativeai as genai

# Configure the Gemini API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

# Configure the Gemini API
genai.configure(api_key=GEMINI_API_KEY)

def generate_image(prompt: str, output_filename: str = None) -> str:
    """
    Generate an image using Gemini's image generation capabilities.
    
    Args:
        prompt (str): Text prompt describing the image to generate
        output_filename (str, optional): Base filename for the output image
        
    Returns:
        str: Path to the generated image file
    """
    try:
        # Create a temporary file if no filename is provided
        if not output_filename:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            output_filename = temp_file.name
            temp_file.close()
        else:
            output_filename = f"{output_filename}.png"
        
        # Generate content and save the image
        print(f"Generating image for prompt: {prompt}")
        
        # Generate the image
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(
            contents=[prompt],
            generation_config={
                "temperature": 0.4,
                "top_p": 1,
                "top_k": 32,
                "max_output_tokens": 2048,
                "response_mime_type": "image/png"
            },
            stream=False
        )
        
        # Check if we have a valid response with image data
        if response and hasattr(response, 'parts'):
            for part in response.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    with open(output_filename, "wb") as f:
                        f.write(part.inline_data.data)
                    print(f"Image saved to: {output_filename}")
                    return output_filename
        
        # Fallback approach if the response structure is different
        # This is a simpler approach as a backup
        try:
            if response and hasattr(response, 'candidates') and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, 'content') and candidate.content:
                        for part in candidate.content.parts:
                            if hasattr(part, 'inline_data') and part.inline_data:
                                with open(output_filename, "wb") as f:
                                    f.write(part.inline_data.data)
                                print(f"Image saved to: {output_filename} (fallback)")
                                return output_filename
        except Exception as inner_e:
            print(f"Inner error handling response: {inner_e}")
            
        # If we reach here, no image was generated
        print("No image data was received from Gemini.")
        return None
        
    except Exception as e:
        print(f"Error in generate_image: {e}")
        return None

def generate_scene_images(prompts: List[str], style: str = "Cartoon") -> List[str]:
    """
    Generate multiple scene images based on text prompts.
    
    Args:
        prompts (List[str]): List of text prompts for different scenes
        style (str): The visual style for the images
        
    Returns:
        List[str]: List of paths to the generated image files
    """
    image_paths = []
    
    for i, prompt in enumerate(prompts):
        # Enhance prompt with style
        enhanced_prompt = f"Create a {style.lower()} style scene for a story: {prompt}. Ensure the image is detailed, colorful, and suitable for a story visualization."
        
        # Generate image
        image_path = generate_image(enhanced_prompt, f"scene_{i+1}")
        
        if image_path:
            image_paths.append(image_path)
    
    return image_paths