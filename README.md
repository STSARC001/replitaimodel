# AI Story Creator

An AI-powered story generation and video creation pipeline combining Gemini, OpenSora, and Bark AI to produce animated narrated stories.

## Overview

This application uses three powerful AI systems to create animated stories:

1. **Gemini AI** - Creates engaging stories and generates prompts for scenes
2. **OpenSora** - Transforms text prompts into dynamic video clips
3. **Bark AI** - Converts story text into natural-sounding voice narration

The application combines these elements into a cohesive animated story with narration.

## Features

- **Story Generation**: Automatically generate creative stories with Gemini API
- **Video Creation**: Convert story scenes into video using OpenSora
- **Voice Narration**: Transform text into natural-sounding narration with Bark AI
- **Final Compilation**: Combine all elements into a complete video

## Requirements

- Python 3.8 or higher
- CUDA-capable GPU (recommended for video and audio generation)
- Gemini API key

## Installation

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up your API key as an environment variable:
   ```
   export GEMINI_API_KEY="your_api_key_here"
   ```

## Usage

Run the application:

```bash
streamlit run app.py
