import gradio as gr
import os
from moviepy.editor import VideoFileClip
import tempfile
import requests
from urllib.parse import urlparse

def download_url(url, temp_dir):
    """Download video from URL and return local filepath"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Get filename from URL or use default
        filename = os.path.basename(urlparse(url).path) or "downloaded_video.mp4"
        local_path = os.path.join(temp_dir, filename)
        
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return local_path
    except Exception as e:
        raise Exception(f"Failed to download URL: {str(e)}")

def convert_video_to_audio(input_source, output_format):
    """Convert video file or URL to audio"""
    try:
        # Create a temporary directory to store the output
        with tempfile.TemporaryDirectory() as temp_dir:
            # Handle URL or file input
            if isinstance(input_source, str) and input_source.startswith(('http://', 'https://')):
                video_path = download_url(input_source, temp_dir)
            else:
                # Handle Gradio file object
                if hasattr(input_source, 'name'):
                    video_path = input_source.name
                else:
                    video_path = input_source

            # Load the video file
            video = VideoFileClip(video_path)
            
            # Determine output filename and path
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            output_filename = f"{base_name}.{output_format.lower()}"
            output_path = os.path.join(temp_dir, output_filename)
            
            # Extract audio and save in the desired format
            video.audio.write_audiofile(output_path)
            
            # Close the video file
            video.close()
            
            return output_path
            
    except Exception as e:
        return f"Error: {str(e)}"

# Supported input formats
input_formats = [".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv"]

# Supported output formats
output_formats = ["mp3", "wav", "m4a", "aac", "ogg"]

# Gradio interface
with gr.Blocks() as app:
    gr.Markdown("# Video to Audio Converter")
    gr.Markdown("Convert video files or URLs to audio in various formats")
    
    with gr.Row():
        with gr.Column():
            video_input = gr.Textbox(label="Enter Video URL or Upload File")
            file_upload = gr.File(label="Upload Video File (optional)", file_types=input_formats)
            output_format = gr.Dropdown(choices=output_formats, label="Output Audio Format", value="mp3")
            convert_btn = gr.Button("Convert")
        
        with gr.Column():
            audio_output = gr.Audio(label="Converted Audio", type="filepath")
            download_output = gr.File(label="Download Audio File")
    
    def process_inputs(url, file, format):
        # Use file if uploaded, otherwise use URL
        if file is not None:
            source = file
        elif url.strip():
            source = url
        else:
            raise gr.Error("Please provide a URL or upload a file")
            
        result = convert_video_to_audio(source, format)
        if result.startswith("Error:"):
            raise gr.Error(result)
        return result, result  # Return the same path for both outputs

    convert_btn.click(
        fn=process_inputs,
        inputs=[video_input, file_upload, output_format],
        outputs=[audio_output, download_output]
    )

if __name__ == "__main__":
    app.launch(debug=True)