from flask import Flask, request, send_file, render_template
from werkzeug.utils import secure_filename
from moviepy.editor import VideoFileClip, AudioFileClip
import yt_dlp
from urllib.parse import urlparse
import os
import uuid
import logging

app = Flask(__name__)

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'm4a'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set up logging
logging.basicConfig(level=logging.DEBUG)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def download_video(url):
    filename = f"{uuid.uuid4()}.mp4"
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    ydl_opts = {
        'format': 'best',  # Downloads best quality video+audio
        'outtmpl': video_path,
        'quiet': True,
        'no_warnings': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Verify the downloaded file
        if not os.path.exists(video_path):
            raise Exception("Download failed: File not created")
        if os.path.getsize(video_path) < 1024:  # Arbitrary min size (1KB)
            raise Exception("Downloaded file is too small to be a valid video")
        
        # Test if it’s a valid video file
        try:
            video = VideoFileClip(video_path)
            video.close()
        except Exception as e:
            raise Exception(f"Downloaded file is not a valid video: {str(e)}")
        
        return video_path
    except Exception as e:
        if os.path.exists(video_path):
            os.remove(video_path)  # Clean up invalid file
        raise Exception(f"Error downloading video: {str(e)}")

def convert_to_audio(file_path):
    extension = os.path.splitext(file_path)[1].lower()
    audio_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}.mp3")
    
    try:
        if extension == '.m4a':
            audio = AudioFileClip(file_path)
            audio.write_audiofile(audio_path)
            audio.close()
        else:
            video = VideoFileClip(file_path)
            if video.audio is None:
                raise Exception("No audio track found in video")
            video.audio.write_audiofile(audio_path)
            video.close()
        return audio_path
    except Exception as e:
        raise Exception(f"Error converting to audio: {str(e)}")

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_video():
    file_path = None
    audio_path = None
    
    try:
        video_url = request.form.get('video_url', '').strip()
        
        if video_url and is_valid_url(video_url):
            file_path = download_video(video_url)
            original_filename = os.path.basename(file_path)
        
        elif 'video' in request.files:
            video_file = request.files['video']
            if video_file.filename == '':
                return 'No selected file', 400
            
            if video_file and allowed_file(video_file.filename):
                filename = f"{uuid.uuid4()}_{secure_filename(video_file.filename)}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                video_file.save(file_path)
                original_filename = secure_filename(video_file.filename)
            else:
                return 'Invalid file type', 400
        else:
            return 'No video file or URL provided', 400
        
        audio_path = convert_to_audio(file_path)
        
        response = send_file(
            audio_path,
            as_attachment=True,
            download_name=f"{os.path.splitext(original_filename)[0]}.mp3"
        )
        
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return response
    
    except Exception as e:
        app.logger.error(f"Conversion error: {str(e)}")
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
        return f'Error: {str(e)}', 500

if __name__ == '__main__':
    app.run(port=5020, debug=True)