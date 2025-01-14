from flask import Flask, send_file, request, render_template_string
import sys
import os
import tempfile
import requests
from urllib.parse import urlparse
from moviepy.editor import VideoFileClip

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Video to Audio Converter</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        input[type="text"] {
            width: 100%;
            padding: 8px;
            margin-top: 5px;
        }
        input[type="submit"] {
            background-color: #4CAF50;
            color: white;
            padding: 10px 15px;
            border: none;
            cursor: pointer;
        }
        .error {
            color: red;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <h1>Video to Audio Converter</h1>
    <form action="/convert" method="post">
        <div class="form-group">
            <label for="video_url">Video URL:</label>
            <input type="text" id="video_url" name="video_url" required 
                   placeholder="Enter video URL (e.g., http://example.com/video.mp4)">
        </div>
        <input type="submit" value="Convert to MP3">
    </form>
    {% if error %}
    <div class="error">
        {{ error }}
    </div>
    {% endif %}
</body>
</html>
'''

def download_video(url, output_path):
    """Download video from URL to local file"""
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/convert', methods=['POST'])
def convert():
    video_url = request.form.get('video_url')
    
    if not video_url:
        return render_template_string(HTML_TEMPLATE, 
            error="Please provide a video URL")

    try:
        parsed = urlparse(video_url)
        if not all([parsed.scheme, parsed.netloc]):
            return render_template_string(HTML_TEMPLATE, 
                error="Invalid URL format")

        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            video_path = os.path.join(temp_dir, 'video_file')
            audio_path = os.path.join(temp_dir, 'audio_file.mp3')
            
            # Download video
            print(f"Downloading video from {video_url}")
            download_video(video_url, video_path)
            
            # Convert to audio
            print("Converting video to audio")
            video = VideoFileClip(video_path)
            video.audio.write_audiofile(audio_path)
            video.close()
            
            # Send the audio file
            return send_file(
                audio_path,
                as_attachment=True,
                download_name='converted_audio.mp3',
                mimetype='audio/mpeg'
            )

    except requests.exceptions.RequestException as e:
        return render_template_string(HTML_TEMPLATE, 
            error=f"Failed to download video: {str(e)}")
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, 
            error=f"An error occurred: {str(e)}")

if __name__ == '__main__':
    # Print debugging information at startup
    print(f"Python version: {sys.version}")
    print(f"Python path: {sys.path}")
    print("MoviePy version:", VideoFileClip.__module__)
    app.run(debug=True)