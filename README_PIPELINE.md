# Automated AI Content Generation Pipeline

This project provides a fully automated pipeline for generating AI-powered stories and illustrations using Google's Gemini API.

## Features

- **Fully Automated**: Generate content without manual intervention
- **Configurable**: Customize themes, styles, and generation parameters
- **Schedulable**: Run the pipeline at scheduled intervals
- **High-Quality Output**: Professional-level stories and illustrations
- **Structured Output**: Organized directory structure for generated content

## Requirements

- Python 3.9+
- Gemini API key (set as environment variable `GEMINI_API_KEY`)

## Files

- `automated_content_pipeline.py`: Main pipeline script for content generation
- `schedule_pipeline.py`: Script for scheduling automatic runs
- `pipeline_config.json`: Configuration file for pipeline settings
- `gemini_generator.py`: Script for story generation using Gemini
- `gemini_image_generator.py`: Script for image generation using Gemini

## Getting Started

1. Ensure your Gemini API key is set as an environment variable:
   ```
   export GEMINI_API_KEY=your_api_key_here
   ```

2. Install required dependencies:
   ```
   pip install google-generativeai streamlit schedule
   ```

3. Run the pipeline manually:
   ```
   python automated_content_pipeline.py
   ```

## Configuration

Edit `pipeline_config.json` to customize the content generation:

```json
{
  "themes": ["Adventure", "Fantasy", "Science Fiction"],
  "styles": ["Cartoon", "Realistic", "Watercolor"],
  "default_style": "Cartoon",
  "num_scenes": 5,
  "target_audience": "All Ages",
  "story_length": "Medium",
  "random_theme_selection": true
}
```

## Scheduling

The pipeline can be scheduled to run automatically:

```
# Run every 2 hours
python schedule_pipeline.py --interval 2 --units hours

# Run daily at 10:00 AM
python schedule_pipeline.py --interval 1 --units days --at "10:00"

# Generate 5 stories per run
python schedule_pipeline.py --interval 1 --units days --num-stories 5
```

## Advanced Usage

### Custom Output Directory

```
python automated_content_pipeline.py --output-dir custom_content
```

### Batch Generation

```
python automated_content_pipeline.py --num-stories 10
```

### Specific Theme or Style

```
python automated_content_pipeline.py --theme "Science Fiction" --style "Realistic"
```

## Output Structure

The pipeline creates a structured output directory:

```
generated_content/
├── science_fiction_20230524_123045/
│   ├── science_fiction_20230524_123045_story.txt
│   ├── science_fiction_20230524_123045_scene_1.png
│   ├── science_fiction_20230524_123045_scene_2.png
│   ├── science_fiction_20230524_123045_scene_3.png
│   └── science_fiction_20230524_123045_metadata.json
└── adventure_20230524_130512/
    ├── adventure_20230524_130512_story.txt
    ├── adventure_20230524_130512_scene_1.png
    ├── adventure_20230524_130512_scene_2.png
    └── adventure_20230524_130512_metadata.json
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.