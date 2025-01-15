from flask import Flask, request, send_file, render_template
from werkzeug.utils import secure_filename
from moviepy.editor import VideoFileClip
from urllib.parse import urlparse
import yt_dlp
import os
import uuid

app = Flask(__name__)

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'flv'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def download_video(url):
    # Generate a unique filename
    filename = f"{uuid.uuid4()}.mp4"
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    ydl_opts = {
        'format': 'best',  # Download best quality
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
    audio_path = os.path.join(
        app.config['UPLOAD_FOLDER'],
        f"{os.path.splitext(os.path.basename(video_path))[0]}.mp3"
    )
    
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)
    video.close()
    
    return audio_path

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_video():
    video_path = None
    audio_path = None
    
    try:
        # Check if URL is provided
        video_url = request.form.get('video_url', '').strip()
        
        if video_url and is_valid_url(video_url):
            # Handle URL-based video
            video_path = download_video(video_url)
            filename = os.path.basename(video_path)
        
        elif 'video' in request.files:
            # Handle file upload
            video_file = request.files['video']
            if video_file.filename == '':
                return 'No selected file', 400
            
            if video_file and allowed_file(video_file.filename):
                filename = secure_filename(video_file.filename)
                video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                video_file.save(video_path)
            else:
                return 'Invalid file type', 400
        else:
            return 'No video file or URL provided', 400
        
        # Convert to audio
        audio_path = convert_to_audio(video_path)
        
        # Clean up the video file
        if os.path.exists(video_path):
            os.remove(video_path)
        
        # Send the audio file
        return send_file(
            audio_path,
            as_attachment=True,
            download_name=f"{os.path.splitext(filename)[0]}.mp3"
        )
    
    except Exception as e:
        # Clean up files in case of error
        if video_path and os.path.exists(video_path):
            os.remove(video_path)
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
        return f'Error: {str(e)}', 500
    
    finally:
        # Clean up the audio file after sending
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)

if __name__ == '__main__':
    app.run(debug=True)