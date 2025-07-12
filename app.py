#!/usr/bin/env python3
"""
YouTube to MP3 Converter

A simple script to download audio from YouTube videos and convert to MP3.
Usage: python converter.py <youtube_url>
"""

import os
import sys
import tempfile
import shutil
import re
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    print("❌ yt-dlp is not installed. Install it with:")
    print("pip install yt-dlp")
    sys.exit(1)

def is_valid_youtube_url(url):
    """Check if URL is a valid YouTube URL"""
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )
    return bool(re.match(youtube_regex, url))

def download_youtube_audio(video_url, output_file='converted.mp3'):
    """
    Download audio from YouTube video and convert to MP3
    
    Args:
        video_url (str): YouTube video URL
        output_file (str): Output filename (default: 'converted.mp3')
    
    Returns:
        str: Path to the converted MP3 file
    """
    
    # Validate URL
    if not is_valid_youtube_url(video_url):
        raise ValueError("Invalid YouTube URL format")
    
    # Create temporary directory for processing
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Configure yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',  # Download best available audio
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',  # 192 kbps MP3
            }],
            'outtmpl': os.path.join(temp_dir, 'temp_audio.%(ext)s'),
            'quiet': True,  # Suppress most output
            'no_warnings': True,
            'extract_flat': False,
            'socket_timeout': 30,
            'retries': 3,
        }
        
        print(f"📥 Downloading audio from: {video_url}")
        
        # Download and convert
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # Extract video info first
                info = ydl.extract_info(video_url, download=False)
                
                if not info:
                    raise Exception("Could not extract video information")
                
                # Check if it's a live stream
                if info.get('is_live', False):
                    raise Exception("Live streams are not supported")
                
                # Print video info
                title = info.get('title', 'Unknown')
                duration = info.get('duration', 0)
                
                print(f"📺 Title: {title}")
                if duration:
                    minutes = duration // 60
                    seconds = duration % 60
                    print(f"⏱️  Duration: {minutes}:{seconds:02d}")
                
                # Download the audio
                ydl.download([video_url])
                
            except yt_dlp.utils.DownloadError as e:
                error_str = str(e)
                if "Private video" in error_str:
                    raise Exception("This is a private video")
                elif "Video unavailable" in error_str:
                    raise Exception("Video is unavailable")
                elif "Sign in to confirm your age" in error_str:
                    raise Exception("Age-restricted video")
                else:
                    raise Exception(f"Download failed: {error_str}")
        
        # Find the converted MP3 file
        mp3_file = None
        for file in os.listdir(temp_dir):
            if file.endswith('.mp3'):
                mp3_file = os.path.join(temp_dir, file)
                break
        
        if not mp3_file or not os.path.exists(mp3_file):
            raise Exception("MP3 conversion failed - no output file found")
        
        # Move the file to the desired location
        final_path = os.path.abspath(output_file)
        shutil.move(mp3_file, final_path)
        
        print(f"✅ Audio converted and saved to: {final_path}")
        return final_path
        
    except Exception as e:
        raise Exception(f"Conversion failed: {str(e)}")
    
    finally:
        # Clean up temporary directory
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"Warning: Could not clean up temp directory: {e}")

def main():
    """Main function with interactive URL input"""
    try:
        print("🎵 YouTube to MP3 Converter")
        print("=" * 40)
        
        # Get YouTube URL from user
        while True:
            video_url = input("\nEnter YouTube URL: ").strip()
            if not video_url:
                print("Please enter a valid URL")
                continue
            if not is_valid_youtube_url(video_url):
                print("Invalid YouTube URL format. Please enter a valid YouTube URL.")
                continue
            break
        
        print()  # Add spacing
        
        # Convert the video
        output_file = download_youtube_audio(video_url)
        
        # Get file size
        file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
        print(f"📄 File size: {file_size:.1f} MB")
        
        print("\n🎉 Conversion completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()