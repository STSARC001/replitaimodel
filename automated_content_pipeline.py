#!/usr/bin/env python3
"""
Automated Content Creation Pipeline

This script automates the entire process of story generation and image creation
using Google's Gemini AI. It can be scheduled to run at regular intervals or triggered
by external events.

Features:
- Automatically generates story content based on configurable themes
- Creates corresponding images for key scenes in the story
- Saves all generated content to designated output folders
- Logs activities and generates reports
"""

import os
import sys
import time
import logging
import random
import json
from datetime import datetime
from typing import List, Dict, Tuple, Any
import argparse

# Import the generation modules
from gemini_generator import generate_story, generate_story_image_prompts
from gemini_image_generator import generate_scene_images

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("content_pipeline.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ContentPipeline")

# Themes configuration - can be expanded or loaded from a JSON file
DEFAULT_THEMES = [
    "Adventure", "Fantasy", "Science Fiction", "Mystery", 
    "Fairy Tale", "Fable", "Educational", "Superhero", 
    "Space Exploration", "Underwater Adventure", "Time Travel", 
    "Historical", "Animal Friends", "Magical Creatures"
]

# Style configuration
STYLES = ["Cartoon", "Realistic", "Watercolor", "Digital Art", "3D Render"]

class ContentPipeline:
    """
    A class to handle the automated content creation pipeline.
    """
    
    def __init__(self, output_dir: str = "generated_content", config_file: str = None):
        """
        Initialize the content pipeline.
        
        Args:
            output_dir (str): Directory to save generated content
            config_file (str, optional): Path to configuration file
        """
        self.output_dir = output_dir
        self.config = self._load_config(config_file)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "stories"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "images"), exist_ok=True)
        
        # Check if API keys are available
        if not os.environ.get("GEMINI_API_KEY"):
            logger.error("GEMINI_API_KEY environment variable is not set")
            raise ValueError("GEMINI_API_KEY environment variable is not set")
    
    def _load_config(self, config_file: str = None) -> Dict[str, Any]:
        """
        Load configuration from file or use defaults.
        
        Args:
            config_file (str, optional): Path to configuration file
            
        Returns:
            Dict[str, Any]: Configuration dictionary
        """
        default_config = {
            "themes": DEFAULT_THEMES,
            "styles": STYLES,
            "default_style": "Cartoon",
            "num_scenes": 5,
            "target_audience": "All Ages",
            "story_length": "Medium",
            "random_theme_selection": True,
            "save_json_metadata": True
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    custom_config = json.load(f)
                    logger.info(f"Loaded configuration from {config_file}")
                    # Update default config with custom values
                    default_config.update(custom_config)
            except Exception as e:
                logger.error(f"Error loading config file: {e}")
        
        return default_config
    
    def generate_content(self, theme: str = None, style: str = None) -> Dict[str, Any]:
        """
        Generate a complete set of content including story and images.
        
        Args:
            theme (str, optional): Story theme to use
            style (str, optional): Visual style for images
            
        Returns:
            Dict[str, Any]: Content generation results
        """
        # Use provided values or ones from config
        theme = theme or (random.choice(self.config["themes"]) if self.config["random_theme_selection"] else self.config["themes"][0])
        style = style or self.config["default_style"]
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        content_id = f"{theme.lower().replace(' ', '_')}_{timestamp}"
        
        logger.info(f"Starting content generation: theme='{theme}', style='{style}'")
        
        try:
            # Step 1: Generate story content
            story_prompt = self._create_story_prompt(theme)
            logger.info(f"Generating story with prompt: {story_prompt}")
            
            story_title, story_text = generate_story(story_prompt)
            logger.info(f"Story generated: '{story_title}'")
            
            # Step 2: Generate image prompts from the story
            logger.info("Generating image prompts")
            image_prompts = generate_story_image_prompts(
                story_text, 
                style
            )[:self.config["num_scenes"]]
            
            logger.info(f"Generated {len(image_prompts)} image prompts")
            
            # Step 3: Generate images for each scene
            logger.info(f"Generating {len(image_prompts)} scene images")
            image_paths = generate_scene_images(image_prompts, style)
            logger.info(f"Generated {len(image_paths)} images")
            
            # Step 4: Save all the content
            content_data = self._save_content(content_id, story_title, story_text, image_prompts, image_paths)
            
            return content_data
            
        except Exception as e:
            logger.error(f"Error in content generation: {e}")
            return {
                "error": str(e),
                "content_id": content_id,
                "timestamp": timestamp,
                "success": False
            }
    
    def _create_story_prompt(self, theme: str) -> str:
        """
        Create a detailed story generation prompt.
        
        Args:
            theme (str): The story theme
            
        Returns:
            str: Complete story prompt
        """
        # Construct story prompt
        story_prompt = f"Create a {self.config['story_length'].lower()} {theme.lower()} story for {self.config['target_audience'].lower()} audience"
        
        # Add any additional customizations from config
        if "additional_prompt_text" in self.config:
            story_prompt += f". {self.config['additional_prompt_text']}"
            
        return story_prompt
    
    def _save_content(self, content_id: str, title: str, story: str, prompts: List[str], image_paths: List[str]) -> Dict[str, Any]:
        """
        Save all generated content to the output directory.
        
        Args:
            content_id (str): Unique identifier for this content
            title (str): Story title
            story (str): Full story text
            prompts (List[str]): Image prompts
            image_paths (List[str]): Paths to generated images
            
        Returns:
            Dict[str, Any]: Content metadata
        """
        # Create a directory for this specific content
        content_dir = os.path.join(self.output_dir, content_id)
        os.makedirs(content_dir, exist_ok=True)
        
        # Save story text
        story_file = os.path.join(content_dir, f"{content_id}_story.txt")
        with open(story_file, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n{story}")
        
        # Save images to content directory
        saved_image_paths = []
        for i, image_path in enumerate(image_paths):
            if image_path and os.path.exists(image_path):
                new_image_name = f"{content_id}_scene_{i+1}.png"
                new_image_path = os.path.join(content_dir, new_image_name)
                
                # Copy the image file
                import shutil
                shutil.copy2(image_path, new_image_path)
                saved_image_paths.append(new_image_path)
        
        # Create metadata
        metadata = {
            "content_id": content_id,
            "timestamp": datetime.now().isoformat(),
            "title": title,
            "story_file": story_file,
            "image_files": saved_image_paths,
            "image_prompts": prompts,
            "success": True
        }
        
        # Save metadata if configured
        if self.config.get("save_json_metadata", True):
            metadata_file = os.path.join(content_dir, f"{content_id}_metadata.json")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
        
        logger.info(f"Content saved to {content_dir}")
        return metadata
    
    def run_batch(self, num_stories: int = 1, themes: List[str] = None, styles: List[str] = None) -> List[Dict[str, Any]]:
        """
        Run a batch of content generation tasks.
        
        Args:
            num_stories (int): Number of stories to generate
            themes (List[str], optional): List of themes to use (randomly selected if not provided)
            styles (List[str], optional): List of styles to use (randomly selected if not provided)
            
        Returns:
            List[Dict[str, Any]]: List of content generation results
        """
        results = []
        
        themes = themes or self.config["themes"]
        styles = styles or self.config["styles"]
        
        logger.info(f"Starting batch generation of {num_stories} stories")
        
        for i in range(num_stories):
            theme = random.choice(themes) if themes else None
            style = random.choice(styles) if styles else None
            
            logger.info(f"Generating content {i+1}/{num_stories}")
            result = self.generate_content(theme, style)
            results.append(result)
        
        # Generate batch summary
        success_count = sum(1 for r in results if r.get("success", False))
        logger.info(f"Batch completed: {success_count}/{len(results)} successful generations")
        
        return results


def main():
    """
    Main function to run the content pipeline.
    """
    parser = argparse.ArgumentParser(description="Automated Content Creation Pipeline")
    parser.add_argument("--output-dir", default="generated_content", help="Output directory for generated content")
    parser.add_argument("--config", help="Path to configuration file (JSON)")
    parser.add_argument("--num-stories", type=int, default=1, help="Number of stories to generate")
    parser.add_argument("--theme", help="Specific theme to use (overrides config)")
    parser.add_argument("--style", help="Specific style to use (overrides config)")
    
    args = parser.parse_args()
    
    try:
        # Initialize the pipeline
        pipeline = ContentPipeline(output_dir=args.output_dir, config_file=args.config)
        
        if args.num_stories > 1:
            # Batch mode
            results = pipeline.run_batch(args.num_stories)
            print(f"Generated {len(results)} content packages")
        else:
            # Single story mode
            result = pipeline.generate_content(args.theme, args.style)
            
            if result.get("success", False):
                print(f"Content successfully generated: {result['title']}")
                print(f"Files saved to: {os.path.join(args.output_dir, result['content_id'])}")
            else:
                print(f"Content generation failed: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        logger.error(f"Pipeline execution error: {e}")
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())