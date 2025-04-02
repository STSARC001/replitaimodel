import os
import tempfile
import torch
import torch.nn as nn
import numpy as np
import imageio
from typing import Optional, List, Union

# Global variables for model storage
MODEL_LOADED = False
TRANSFORMER_MODEL = None
VAE_MODEL = None
TEXT_ENCODER = None
TOKENIZER = None
VIDEOGEN_PIPELINE = None

def load_opensora_models():
    """Load OpenSora models if they haven't been loaded yet"""
    global MODEL_LOADED, TRANSFORMER_MODEL, VAE_MODEL, TEXT_ENCODER, TOKENIZER, VIDEOGEN_PIPELINE
    
    if not MODEL_LOADED:
        try:
            import torch
            from diffusers import PNDMScheduler
            from transformers import T5Tokenizer, T5EncoderModel
            
            # Import OpenSora components (assuming they're installed)
            from opensora.models.ae import ae_stride_config, getae, getae_wrapper
            from opensora.models.diffusion.latte.modeling_latte import LatteT2V
            from opensora.sample.pipeline_videogen import VideoGenPipeline
            
            # Define arguments similar to the sample file
            args = type('args', (), {
                'ae': 'CausalVAEModel_4x8x8',
                'force_images': False,
                'model_path': 'LanguageBind/Open-Sora-Plan-v1.0.0',
                'text_encoder_name': 'DeepFloyd/t5-v1_1-xxl',
                'version': '16x512x512'  # Using a shorter video length for faster generation
            })
            
            device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
            
            # Load model components
            print("Loading OpenSora transformer model...")
            TRANSFORMER_MODEL = LatteT2V.from_pretrained(
                args.model_path, 
                subfolder=args.version, 
                torch_dtype=torch.float16, 
                cache_dir='cache_dir'
            ).to(device)
            
            print("Loading OpenSora VAE model...")
            VAE_MODEL = getae_wrapper(args.ae)(
                args.model_path, 
                subfolder="vae", 
                cache_dir='cache_dir'
            ).to(device, dtype=torch.float16)
            
            VAE_MODEL.vae.enable_tiling()
            image_size = int(args.version.split('x')[1])
            latent_size = (image_size // ae_stride_config[args.ae][1], image_size // ae_stride_config[args.ae][2])
            VAE_MODEL.latent_size = latent_size
            TRANSFORMER_MODEL.force_images = args.force_images
            
            print("Loading text encoder and tokenizer...")
            TOKENIZER = T5Tokenizer.from_pretrained(
                args.text_encoder_name, 
                cache_dir="cache_dir"
            )
            
            TEXT_ENCODER = T5EncoderModel.from_pretrained(
                args.text_encoder_name, 
                cache_dir="cache_dir",
                torch_dtype=torch.float16
            ).to(device)
            
            # Set eval mode for all models
            TRANSFORMER_MODEL.eval()
            VAE_MODEL.eval()
            TEXT_ENCODER.eval()
            
            # Create the pipeline
            scheduler = PNDMScheduler()
            VIDEOGEN_PIPELINE = VideoGenPipeline(
                vae=VAE_MODEL,
                text_encoder=TEXT_ENCODER,
                tokenizer=TOKENIZER,
                scheduler=scheduler,
                transformer=TRANSFORMER_MODEL
            ).to(device=device)
            
            MODEL_LOADED = True
            print("OpenSora models loaded successfully")
            
        except Exception as e:
            print(f"Error loading OpenSora models: {e}")
            raise

def map_style_to_prompt_prefix(style: str) -> str:
    """
    Map the style selection to a prefix for the prompt to guide the video generation.
    
    Args:
        style (str): The selected style
        
    Returns:
        str: A prefix string to guide the style
    """
    style_map = {
        "Realistic": "photorealistic, highly detailed, 4k resolution",
        "Cartoon": "cartoon style, colorful, animation",
        "Anime": "anime style, 2D animation, Japanese animation style",
        "Watercolor": "watercolor painting style, artistic, flowing colors",
        "3D Animation": "3D animation, rendered, Pixar style"
    }
    
    return style_map.get(style, "high quality")

def generate_video(prompt: str, style: str = "Realistic", 
                  sample_steps: int = 50, guidance_scale: float = 10.0, 
                  force_images: bool = False) -> str:
    """
    Generate a video clip using OpenSora based on a text prompt.
    
    Args:
        prompt (str): The text prompt describing the desired video
        style (str): The style of video to generate
        sample_steps (int): Number of sampling steps (higher = better quality but slower)
        guidance_scale (float): Guidance scale for generation (higher = more prompt adherence)
        force_images (bool): If True, generate a single image instead of video
        
    Returns:
        str: Path to the generated video file
    """
    try:
        # Load models if not already loaded
        if not MODEL_LOADED:
            load_opensora_models()
            
        # Enhance prompt with style
        style_prefix = map_style_to_prompt_prefix(style)
        enhanced_prompt = f"{style_prefix}, {prompt}"
        
        # Set parameters
        device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        video_length = 1 if force_images else TRANSFORMER_MODEL.config.video_length
        height, width = 512, 512
        num_frames = 1 if video_length == 1 else 16  # Using shorter videos for faster generation
        
        print(f"Generating video for prompt: {enhanced_prompt}")
        print(f"Parameters: steps={sample_steps}, guidance={guidance_scale}, frames={num_frames}")
        
        # Generate video
        with torch.no_grad():
            videos = VIDEOGEN_PIPELINE(
                enhanced_prompt,
                video_length=video_length,
                height=height,
                width=width,
                num_inference_steps=sample_steps,
                guidance_scale=guidance_scale,
                enable_temporal_attentions=not force_images,
                num_images_per_prompt=1,
                mask_feature=True,
            ).video
        
        # Clear CUDA cache to free memory
        torch.cuda.empty_cache()
        
        # Get the video data
        video_data = videos[0]
        
        # Save to a temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        imageio.mimwrite(temp_file.name, video_data, fps=24, quality=7)
        
        return temp_file.name
        
    except Exception as e:
        print(f"Error in generate_video: {e}")
        
        # Create a simple error video or return path to a default video
        temp_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        # Create a black frame as a fallback
        black_frame = np.zeros((512, 512, 3), dtype=np.uint8)
        frames = [black_frame] * 24  # 1 second at 24fps
        imageio.mimwrite(temp_file.name, frames, fps=24)
        
        return temp_file.name
