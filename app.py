from flask import Flask, request, send_file
from moviepy.editor import VideoFileClip

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']

    if file.filename == '':
        return 'No selected file', 400

    if file:
        try:
            # Save the uploaded video temporarily
            video_path = 'uploads/' + file.filename
            file.save(video_path)

            # Convert video to audio using moviepy
            video_clip = VideoFileClip(video_path)
            audio_clip = video_clip.audio
            audio_path = 'downloads/' + file.filename.replace('.mp4', '.mp3')  # Adjust for different video extensions
            audio_clip.write_audiofile(audio_path)

            # Send the converted audio file
            return send_file(audio_path, as_attachment=True)

        except Exception as e:
            return f"An error occurred: {str(e)}", 500

    return 'Something went wrong', 500

if __name__ == '__main__':
    app.run(debug=True)
