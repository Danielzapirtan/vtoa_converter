import gradio as gr
import os
from moviepy.editor import VideoFileClip
import tempfile

def convert_video_to_audio(video_file, output_format):
    try:
        # Create a temporary directory to store the output
        with tempfile.TemporaryDirectory() as temp_dir:
            # Load the video file
            video = VideoFileClip(video_file.name)
            
            # Determine output filename and path
            base_name = os.path.splitext(os.path.basename(video_file.name))[0]
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
output_formats = ["MP3", "WAV", "M4A", "AAC", "OGG"]

# Gradio interface
with gr.Blocks() as app:
    gr.Markdown("# Video to Audio Converter")
    gr.Markdown("Convert video files to audio in various formats")
    
    with gr.Row():
        with gr.Column():
            video_input = gr.File(label="Upload Video File", file_types=input_formats)
            output_format = gr.Dropdown(choices=output_formats, label="Output Audio Format", value="MP3")
            convert_btn = gr.Button("Convert")
        
        with gr.Column():
            audio_output = gr.Audio(label="Converted Audio", type="filepath")
            download_output = gr.File(label="Download Audio File")
    
    convert_btn.click(
        fn=convert_video_to_audio,
        inputs=[video_input, output_format],
        outputs=[audio_output, download_output]
    )

if __name__ == "__main__":
    app.launch(debug=True)