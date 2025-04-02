import os
import tempfile
import streamlit as st
from typing import Union

def create_progress_bar(initial_value: float = 0, text: str = "Processing...") -> st.progress:
    """
    Create a Streamlit progress bar with initial value and text.
    
    Args:
        initial_value (float): Initial progress value (0-100)
        text (str): Text to display with the progress bar
        
    Returns:
        st.progress: Streamlit progress bar component
    """
    progress_bar = st.progress(0, text=text)
    if initial_value > 0:
        progress_bar.progress(initial_value, text=text)
    return progress_bar

def save_text_to_file(text: str) -> str:
    """
    Save text content to a temporary file.
    
    Args:
        text (str): Text content to save
        
    Returns:
        str: Path to the saved file
    """
    temp_file = tempfile.NamedTemporaryFile(suffix=".txt", delete=False)
    with open(temp_file.name, 'w', encoding='utf-8') as f:
        f.write(text)
    return temp_file.name

def check_api_keys() -> bool:
    """
    Check if all required API keys are available in environment variables.
    
    Returns:
        bool: True if all required keys are present, False otherwise
    """
    required_keys = ["GEMINI_API_KEY"]
    
    missing_keys = [key for key in required_keys if not os.environ.get(key)]
    
    if missing_keys:
        st.error(f"Missing required API keys: {', '.join(missing_keys)}")
        st.info("Please set these environment variables before running the application.")
        return False
    
    return True

def format_time_display(seconds: int) -> str:
    """
    Format seconds into a readable time display (MM:SS).
    
    Args:
        seconds (int): Time in seconds
        
    Returns:
        str: Formatted time string
    """
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes:02d}:{remaining_seconds:02d}"

def get_file_extension(filename: str) -> str:
    """
    Get the file extension from a filename.
    
    Args:
        filename (str): Path to file
        
    Returns:
        str: File extension
    """
    return os.path.splitext(filename)[1].lower()
