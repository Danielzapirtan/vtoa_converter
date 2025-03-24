import gradio as gr
from moviepy.editor import VideoFileClip  # Correct import statement
import yt_dlp
import os
import uuid
from urllib.parse import urlparse  # Added import for urlparse

# Configure upload folder
UPLOAD_FOLDER = '/tmp/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'flv'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def download_video(url):
    filename = f"{uuid.uuid4()}.mp4"
    video_path = os.path.join(UPLOAD_FOLDER, filename)
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': video_path,
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return video_path
    except Exception as e:
        raise Exception(f"Error downloading video: {str(e)}")

def convert_to_audio(video_path):
    audio_path = os.path.join(UPLOAD_FOLDER, f"{os.path.splitext(os.path.basename(video_path))[0]}.mp3")
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)
    video.close()
    return audio_path

def process_video(video_file, video_url):
    video_path = None
    audio_path = None
    
    try:
        if video_url:
            if not is_valid_url(video_url):  # Validate URL
                return "Invalid URL provided"
            video_path = download_video(video_url)
        elif video_file:
            if not allowed_file(video_file.name):
                return "Invalid file type"
            video_path = video_file.name
        else:
            return "No video file or URL provided"
        
        audio_path = convert_to_audio(video_path)
        return audio_path
    
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        if video_path and os.path.exists(video_path):
            os.remove(video_path)

# Gradio Interface
iface = gr.Interface(
    fn=process_video,
    inputs=[
        gr.File(label="Upload Video File"),
        gr.Textbox(label="Or Enter Video URL")
    ],
    outputs=gr.Audio(label="Converted Audio"),
    title="Video to Audio Converter",
    description="Upload a video file or provide a video URL to convert it to audio."
)

iface.launch(debug=True)