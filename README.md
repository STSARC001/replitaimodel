# Automatic AI Story Creator

An AI-powered story generation and visualization system that creates animated stories with text and images through a streamlined interface, requiring minimal user input.

## Features

- **Fully Automated**: Stories generate automatically when you select a theme
- **AI-Powered Story Generation**: Uses Google's Gemini AI to create engaging stories
- **Scene Visualization**: Automatically generates images for key scenes in the story
- **Multiple Themes**: Choose from adventure, fantasy, science fiction, and more
- **Customizable**: Add your own custom theme

## Technologies Used

- **Streamlit**: For the web interface
- **Google Gemini API**: For story generation and image creation
- **Python**: Core programming language

## Getting Started

### Prerequisites

- Python 3.8+
- Gemini API key

### Installation

1. Clone the repository
   ```
   git clone https://github.com/yourusername/ai-story-creator.git
   cd ai-story-creator
   ```

2. Install dependencies
   ```
   pip install -r requirements.txt
   ```

3. Set up your API keys
   - Create a `.env` file or set environment variables:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   ```

4. Run the application
   ```
   streamlit run app.py
   ```

## Usage

1. Select a theme from the dropdown menu in the sidebar
2. The application will automatically generate a story based on your selection
3. After the story is generated, images for key scenes will be created
4. View the story text and download generated images

## Future Enhancements

- Add voice narration using Bark AI
- Implement video generation with OpenSora
- Add more customization options
- Support for longer stories with more scenes

## License

This project is licensed under the MIT License - see the LICENSE file for details.