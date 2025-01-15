from flask import Flask, request, send_file, render_template
from werkzeug.utils import secure_filename
from moviepy.editor import VideoFileClip
import os

app = Flask(__name__)

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'flv'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_video():
    if 'video' not in request.files:
        return 'No video file uploaded', 400
    
    video_file = request.files['video']
    
    if video_file.filename == '':
        return 'No selected file', 400
    
    if video_file and allowed_file(video_file.filename):
        # Secure the filename and create paths
        filename = secure_filename(video_file.filename)
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], 
                                 f"{os.path.splitext(filename)[0]}.mp3")
        
        # Save the uploaded video
        video_file.save(video_path)
        
        try:
            # Convert video to audio
            video = VideoFileClip(video_path)
            video.audio.write_audiofile(audio_path)
            video.close()
            
            # Clean up the video file
            os.remove(video_path)
            
            # Send the audio file
            return send_file(
                audio_path,
                as_attachment=True,
                download_name=f"{os.path.splitext(filename)[0]}.mp3"
            )
        
        except Exception as e:
            # Clean up files in case of error
            if os.path.exists(video_path):
                os.remove(video_path)
            if os.path.exists(audio_path):
                os.remove(audio_path)
            return f'Error converting video: {str(e)}', 500
        
        finally:
            # Clean up the audio file after sending
            if os.path.exists(audio_path):
                os.remove(audio_path)
    
    return 'Invalid file type', 400

if __name__ == '__main__':
    app.run(debug=True)
