import os
import sys
from pathlib import Path

from pytube import YouTube
from moviepy.editor import AudioFileClip, VideoFileClip


def download_youtube_video(url: str, out_dir: Path) -> Path:
    """
    Download the highest‑resolution progressive stream (contains video+audio)
    from the given YouTube URL.
    Returns the path to the downloaded .mp4 file.
    """
    try:
        yt = YouTube(url)
    except Exception as e:
        print(f"❌ Failed to parse YouTube URL: {e}")
        sys.exit(1)

    # Choose the highest resolution progressive stream (video+audio together)
    stream = yt.streams.filter(progressive=True, file_extension="mp4") \
                      .order_by("resolution") \
                      .desc() \
                      .first()

    if not stream:
        print("❌ No suitable video stream found.")
        sys.exit(1)

    print(f"Downloading: {yt.title}")
    output_path = stream.download(output_path=str(out_dir))
    return Path(output_path)


def convert_to_mp3(video_path: Path, out_dir: Path) -> Path:
    """
    Extract the audio from the video file and write it as an MP3.
    Returns the path to the created .mp3 file.
    """
    mp3_path = out_dir / f"{video_path.stem}.mp3"

    try:
        # Using VideoFileClip directly extracts the audio track.
        with VideoFileClip(str(video_path)) as clip:
            audio = clip.audio
            if audio is None:
                raise RuntimeError("No audio track found in the video.")
            audio.write_audiofile(str(mp3_path), codec="mp3")
    finally:
        # Close the audio clip to free resources.
        if audio:
            audio.close()

    return mp3_path


def main():
    url = input("Enter a YouTube video URL: ").strip()
    if not url:
        print("❌ No URL provided.")
        return

    cwd = Path.cwd()
    video_file = download_youtube_video(url, cwd)
    print(f"✅ Video saved to: {video_file}")

    mp3_file = convert_to_mp3(video_file, cwd)
    print(f"✅ MP3 saved to: {mp3_file}")

    # Optional: delete the original video to keep only the MP3
    try:
        video_file.unlink()
        print(f"🗑️ Removed temporary video file: {video_file.name}")
    except Exception as e:
        print(f"⚠️ Could not delete temporary video: {e}")


if __name__ == "__main__":
    main()
