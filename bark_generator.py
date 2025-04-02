import os
import torch
import tempfile
import numpy as np
from scipy.io.wavfile import write as write_wav
from typing import Optional, List

# Import Bark components
from bark import SAMPLE_RATE, generate_audio, preload_models

# Global variable to track if models have been loaded
MODELS_LOADED = False

def load_bark_models():
    """Load Bark models if they haven't been loaded yet"""
    global MODELS_LOADED
    if not MODELS_LOADED:
        print("Loading Bark AI models...")
        preload_models()
        MODELS_LOADED = True
        print("Bark AI models loaded successfully")

def prepare_text_for_bark(text: str) -> List[str]:
    """
    Prepare text for Bark by splitting it into manageable chunks.
    Bark works better with shorter segments.
    
    Args:
        text (str): The full text to be narrated
        
    Returns:
        List[str]: A list of text segments suitable for Bark
    """
    # Split by paragraphs
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    
    segments = []
    for paragraph in paragraphs:
        # If paragraph is too long, split it into sentences
        if len(paragraph) > 250:
            sentences = [s.strip() + '.' for s in paragraph.replace('. ', '.||').split('||') if s.strip()]
            
            current_segment = ""
            for sentence in sentences:
                if len(current_segment) + len(sentence) < 250:
                    current_segment += " " + sentence
                else:
                    if current_segment:
                        segments.append(current_segment.strip())
                    current_segment = sentence
            
            if current_segment:
                segments.append(current_segment.strip())
        else:
            segments.append(paragraph)
    
    return segments

def generate_audio_for_segments(segments: List[str], voice_type: str = "Male") -> np.ndarray:
    """
    Generate audio for multiple text segments and concatenate them.
    
    Args:
        segments (List[str]): List of text segments to generate audio for
        voice_type (str): Type of voice to use (Male, Female, Child)
        
    Returns:
        np.ndarray: Concatenated audio array
    """
    # Set the history prompt based on voice type
    if voice_type == "Female":
        history_prompt = "v2/en_speaker_6"  # Female voice
    elif voice_type == "Child":
        history_prompt = "v2/en_speaker_9"  # Child-like voice
    else:
        history_prompt = "v2/en_speaker_1"  # Default male voice
    
    all_audio = []
    
    for i, segment in enumerate(segments):
        print(f"Generating audio for segment {i+1}/{len(segments)}")
        
        # Generate audio for the segment
        audio_array = generate_audio(segment, history_prompt=history_prompt)
        
        # Add a small pause between segments (0.5 seconds of silence)
        silence = np.zeros(int(SAMPLE_RATE * 0.5))
        
        # Append to the combined audio
        all_audio.append(audio_array)
        all_audio.append(silence)
    
    # Concatenate all audio segments
    combined_audio = np.concatenate(all_audio)
    
    return combined_audio

def generate_audio(text: str, voice_type: str = "Male") -> str:
    """
    Generate audio narration for a story using Bark AI.
    
    Args:
        text (str): The text to convert to speech
        voice_type (str): The type of voice to use (Male, Female, Child)
        
    Returns:
        str: Path to the generated audio file
    """
    try:
        # Load models if they haven't been loaded
        load_bark_models()
        
        # Prepare text by breaking it into appropriate segments
        segments = prepare_text_for_bark(text)
        
        # Generate audio for all segments
        combined_audio = generate_audio_for_segments(segments, voice_type)
        
        # Save audio to a temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        write_wav(temp_file.name, SAMPLE_RATE, combined_audio)
        
        return temp_file.name
        
    except Exception as e:
        print(f"Error in generate_audio: {e}")
        
        # Generate a simple error message audio or return a path to a default audio
        error_temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        error_message = "There was an error generating the audio narration."
        error_audio = generate_audio(error_message, "Male")
        
        return error_temp_file.name
