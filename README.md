# AI Story Creator

An AI-powered story generation and image creation application using Gemini AI.

## Overview

This application uses Google's Gemini AI to create engaging stories and visually represent them with generated images:

1. **Story Generation**: Creates engaging, well-structured stories based on your chosen theme, target audience, and characters
2. **Scene Description**: Identifies key scenes from the story that would make compelling visuals
3. **Image Creation**: Uses Gemini 2.0 Flash image generation to create visual representations of each scene

The application provides a simple and intuitive interface to generate and visualize stories for various audiences.

## Features

- **Story Generation**: Automatically generate creative stories with Gemini AI
- **Scene Detection**: Identify the most visually interesting scenes from the story
- **Image Generation**: Create images that represent key moments using Gemini image generation
- **Customizable Settings**: Adjust story themes, audience, length, and visual style
- **Download Support**: Save your favorite images for each scene

## Requirements

- Python 3.8 or higher
- Gemini API key

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install streamlit google-generativeai pillow
   ```
3. Set up your API key as an environment variable:
   ```
   export GEMINI_API_KEY="your_api_key_here"
   ```

## Usage

Run the application:

```bash
streamlit run app.py
```

### Story Parameters

- **Theme**: Choose from Adventure, Fantasy, Science Fiction, Mystery, Fairy Tale, Fable, Educational, or Custom
- **Target Audience**: Select the age group for your story
- **Story Length**: Adjust how long you want your story to be
- **Custom Theme**: Create your own theme for unique stories

### Character Settings

- **Main Character**: Define your story's protagonist
- **Character Traits**: Add personality traits to your character

### Image Settings

- **Image Style**: Choose from visual styles like Realistic, Cartoon, Anime, Watercolor, or 3D Animation
- **Number of Scenes**: Set how many scenes you want to visualize (1-5)

## How It Works

1. The application uses the Gemini AI API to generate a story based on your parameters
2. It analyzes the story to identify key scenes that would make good visuals
3. It sends scene descriptions to Gemini's image generation model
4. It displays the story alongside the generated images for each scene
5. You can download individual scene images for later use
