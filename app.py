import yt_dlp
import os
import time
import browser_cookie3

# Function to download video and convert to MP3
def download_youtube_mp3(url, allow_cookies="y"):
    start_time = time.time()

    # Load cookies automatically from Chrome or Edge if requested
    cookies = None
    try:
        if allow_cookies == "y":
            cookies = browser_cookie3.chrome()  # For Chrome
            # cookies = browser_cookie3.edge()  # Uncomment for Edge
    except Exception as e:
        print(f"Error loading cookies: {e}")
        cookies = None

    if cookies:
        print("Cookies loaded successfully.")

    # yt-dlp options for downloading audio and converting to MP3
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloaded_audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'cookiesfrombrowser': ('chrome',) if cookies else None,  # Pass cookies from Chrome if available
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Find the downloaded file
    mp3_file = next((f for f in os.listdir() if f.startswith("downloaded_audio")), None)

    if not mp3_file:
        print("Error: No MP3 file found.")
        return

    elapsed_time = time.time() - start_time
    print(f"MP3 file downloaded successfully: {mp3_file}")
    print(f"Processing time: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    url = input("Enter YouTube URL: ")
    allow_cookies = input("Do you want to use cookies for authentication (y/n)? ").strip().lower()
    
    download_youtube_mp3(url, allow_cookies)