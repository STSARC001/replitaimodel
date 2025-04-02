import os
import subprocess
import tempfile
from typing import List, Optional

def compile_final_video(video_files: List[str], audio_file: str, title: str) -> str:
    """
    Compile the final video by combining multiple video clips and adding audio narration.
    
    Args:
        video_files (List[str]): List of paths to video clip files
        audio_file (str): Path to audio narration file
        title (str): Title of the story for the opening frame
        
    Returns:
        str: Path to the final compiled video
    """
    try:
        # Create temporary files for intermediate processing
        temp_concat_file = tempfile.NamedTemporaryFile(suffix=".txt", delete=False)
        temp_silent_video = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        final_video_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        
        # Create a concat file for FFmpeg
        with open(temp_concat_file.name, 'w') as f:
            for video_file in video_files:
                f.write(f"file '{video_file}'\n")
        
        # Concatenate videos without audio
        subprocess.run([
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
            '-i', temp_concat_file.name, '-c', 'copy',
            temp_silent_video.name
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Get duration of audio and video
        audio_duration_cmd = [
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', audio_file
        ]
        audio_duration = float(subprocess.check_output(audio_duration_cmd).decode('utf-8').strip())
        
        video_duration_cmd = [
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', temp_silent_video.name
        ]
        video_duration = float(subprocess.check_output(video_duration_cmd).decode('utf-8').strip())
        
        # Decide how to handle timing differences
        if abs(audio_duration - video_duration) > 1.0:  # If difference is more than 1 second
            # Adjust video speed to match audio duration
            speed_factor = video_duration / audio_duration if audio_duration > 0 else 1.0
            
            # Create title card
            title_card = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
            title_text = title.replace("'", "'\\''")  # Escape single quotes for shell
            
            # Generate a title card using FFmpeg
            subprocess.run([
                'ffmpeg', '-y', '-f', 'lavfi', '-i', f"color=c=black:s=512x512:d=3", 
                '-vf', f"drawtext=text='{title_text}':fontcolor=white:fontsize=36:x=(w-text_w)/2:y=(h-text_h)/2",
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', title_card.name
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Create a new concat file including the title card
            new_concat_file = tempfile.NamedTemporaryFile(suffix=".txt", delete=False)
            with open(new_concat_file.name, 'w') as f:
                f.write(f"file '{title_card.name}'\n")
                f.write(f"file '{temp_silent_video.name}'\n")
            
            # Concatenate title card with content video
            temp_with_title = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
            subprocess.run([
                'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
                '-i', new_concat_file.name, '-c', 'copy',
                temp_with_title.name
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Add audio to the combined video
            subprocess.run([
                'ffmpeg', '-y', '-i', temp_with_title.name, '-i', audio_file,
                '-c:v', 'copy', '-c:a', 'aac', '-map', '0:v:0', '-map', '1:a:0',
                '-shortest', final_video_file.name
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Clean up title card temp file
            os.unlink(title_card.name)
            os.unlink(new_concat_file.name)
            
        else:
            # Simply combine video and audio if durations are close
            subprocess.run([
                'ffmpeg', '-y', '-i', temp_silent_video.name, '-i', audio_file,
                '-c:v', 'copy', '-c:a', 'aac', '-map', '0:v:0', '-map', '1:a:0',
                '-shortest', final_video_file.name
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Clean up temporary files
        os.unlink(temp_concat_file.name)
        os.unlink(temp_silent_video.name)
        
        return final_video_file.name
        
    except Exception as e:
        print(f"Error in compile_final_video: {e}")
        
        # Return the first video file as a fallback
        if video_files and os.path.exists(video_files[0]):
            return video_files[0]
        
        # If no video files, create a simple error video
        error_video = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        
        # Create a black screen with error text
        subprocess.run([
            'ffmpeg', '-y', '-f', 'lavfi', '-i', 'color=c=black:s=512x512:d=5', 
            '-vf', "drawtext=text='Error creating video':fontcolor=white:fontsize=36:x=(w-text_w)/2:y=(h-text_h)/2",
            '-c:v', 'libx264', '-pix_fmt', 'yuv420p', error_video.name
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        return error_video.name
