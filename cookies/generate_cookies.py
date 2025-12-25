import os
import yt_dlp

DIR_PATH = os.path.dirname(__file__)

def _check_platform(domain:str)->str:
    platform = "unknown"
    if "youtube.com" in domain or "youtu.be" in domain:
        platform = "youtube"
    elif "twitch.tv" in domain:
        platform = "twitch"
    elif "facebook.com" in domain:
        platform = "facebook"
    elif "instagram.com" in domain:
        platform = "instagram"
    elif "tiktok.com" in domain:
        platform = "tiktok"
    elif "vimeo.com" in domain:
        platform = "vimeo"
    elif "linkedin.com" in domain:
        platform = "linkedin"
    return platform

def create_cookies(url, cookies_file:str):
    ydl_opts = {
        "cookiesfrombrowser": ("edge",),
        "skip_download": True,
        "writeinfojson": False,
        "writesubtitles": False,
        "writethumbnail": False,
        "write_cookies": cookies_file  # <--- this actually saves cookies
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def main():
    platform = _check_platform("https://www.youtube.com")
    file_path = os.path.join(DIR_PATH, f"{platform}.txt")
    create_cookies(url="https://www.youtube.com/watch?v=rnXIjl_Rzy4", cookies_file=file_path)

if __name__ == '__main__':
    main()