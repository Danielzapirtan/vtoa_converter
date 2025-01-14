from flask import Flask, send_file, request, render_template_string
import sys
import os

app = Flask(__name__)

# HTML template for the upload form
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
    {% if debug_info %}
    <pre>{{ debug_info }}</pre>
    {% endif %}
</body>
</html>
'''

@app.route('/')
def index():
    # Add debug information
    debug_info = f"Python version: {sys.version}\n"
    debug_info += f"Python path: {sys.path}\n"
    
    try:
        import moviepy
        debug_info += f"MoviePy version: {moviepy.__version__}\n"
    except ImportError as e:
        debug_info += f"MoviePy import error: {str(e)}\n"
    except Exception as e:
        debug_info += f"MoviePy error: {str(e)}\n"
    
    return render_template_string(HTML_TEMPLATE, error=None, debug_info=debug_info)

@app.route('/convert', methods=['POST'])
def convert():
    try:
        # Try importing required modules
        import moviepy.editor
        import requests
        from urllib.parse import urlparse
        import tempfile
        
        video_url = request.form.get('video_url')
        if not video_url:
            return render_template_string(HTML_TEMPLATE, 
                error="Please provide a video URL")

        # Rest of the conversion logic...
        # (Previous conversion code here)
        
    except ImportError as e:
        return render_template_string(HTML_TEMPLATE, 
            error=f"Import error: {str(e)}. Please ensure all dependencies are installed.")
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, 
            error=f"An error occurred: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)