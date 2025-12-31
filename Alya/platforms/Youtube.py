import asyncio
import os
import re
import json
import time
from typing import Union
import requests
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch
from Alya.utils.database import is_on_off
from Alya import app  # Import userbot here
from Alya.utils.formatters import time_to_seconds
import random
import logging
import aiohttp
from Alya import LOGGER
from urllib.parse import urlparse
from pyrogram import Client
from pyrogram.errors import RPCError
from config import API_KEY
# Your local API server URL
YOUR_API_URL = "http://138.2.101.220:8080"

# File cleanup configuration
CLEANUP_INTERVAL = 6 * 3600  # 6 hours in seconds
DOWNLOAD_DIR = "downloads"

# Initialize cleanup task
_cleanup_task = None

def cookie_txt_file():
    cookie_dir = "AloneMusic/cookies"
    if not os.path.exists(cookie_dir):
        return None
    cookies_files = [f for f in os.listdir(cookie_dir) if f.endswith(".txt")]
    if not cookies_files:
        return None
    cookie_file = os.path.join(cookie_dir, random.choice(cookies_files))
    return cookie_file

async def start_cleanup_task():
    """Start the background cleanup task"""
    global _cleanup_task
    if _cleanup_task is None:
        _cleanup_task = asyncio.create_task(cleanup_old_files())
        LOGGER("AloneMusic/platforms/Youtube.py").info("🔄 File cleanup task started")

async def stop_cleanup_task():
    """Stop the background cleanup task"""
    global _cleanup_task
    if _cleanup_task:
        _cleanup_task.cancel()
        try:
            await _cleanup_task
        except asyncio.CancelledError:
            pass
        _cleanup_task = None
        LOGGER("AloneMusic/platforms/Youtube.py").info("🛑 File cleanup task stopped")

async def cleanup_old_files():
    """Background task to clean up files older than 6 hours"""
    logger = LOGGER("AloneMusic/platforms/Youtube.py")
    
    while True:
        try:
            await asyncio.sleep(3600)  # Check every hour
            
            if not os.path.exists(DOWNLOAD_DIR):
                continue
                
            current_time = time.time()
            deleted_count = 0
            
            for filename in os.listdir(DOWNLOAD_DIR):
                file_path = os.path.join(DOWNLOAD_DIR, filename)
                
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getctime(file_path)
                    
                    if file_age > CLEANUP_INTERVAL:
                        try:
                            os.remove(file_path)
                            deleted_count += 1
                            logger.info(f"🧹 Cleaned up old file: {filename}")
                        except Exception as e:
                            logger.error(f"❌ Error cleaning up {filename}: {e}")
            
            if deleted_count > 0:
                logger.info(f"🗑️ Cleanup completed: {deleted_count} files removed")
                
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"💥 Cleanup task error: {e}")
            await asyncio.sleep(300)  # Wait 5 minutes before retrying on error

def get_file_creation_time(file_path):
    """Get file creation time, fallback to modification time if not available"""
    try:
        return os.path.getctime(file_path)
    except:
        return os.path.getmtime(file_path)

async def check_and_cleanup_file(file_path):
    """Check if a file should be cleaned up and remove it if too old"""
    if not os.path.exists(file_path):
        return
    
    current_time = time.time()
    file_age = current_time - get_file_creation_time(file_path)
    
    if file_age > CLEANUP_INTERVAL:
        try:
            os.remove(file_path)
            LOGGER("AloneMusic/platforms/Youtube.py").info(f"🧹 Auto-cleaned expired file: {os.path.basename(file_path)}")
        except Exception as e:
            LOGGER("AloneMusic/platforms/Youtube.py").error(f"❌ Error auto-cleaning file: {e}")

async def download_direct_from_api(video_id: str, stream_type: str) -> str:
    """Download file directly from API using the stream endpoints"""
    logger = LOGGER("AloneMusic/platforms/Youtube.py")
    
    # Determine endpoint and file extension based on type
    if stream_type == "audio":
        endpoint = f"{YOUR_API_URL}/stream/{video_id}"
        file_ext = "webm"
        filename = f"{video_id}.webm"
    else:
        endpoint = f"{YOUR_API_URL}/video_stream/{video_id}"
        file_ext = "mp4"
        filename = f"{video_id}.mp4"
    
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    
    # Clean up existing file if it exists
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            logger.info(f"🗑️ Removed existing file: {filename}")
        except Exception as e:
            logger.error(f"❌ Error removing existing file: {e}")
    
    # Download directly from API with Bearer token authentication
    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        params = {}
        
        # For audio, we need to set direct=1 to get the actual file
        if stream_type == "audio":
            params["direct"] = 1
        
        async with aiohttp.ClientSession(headers=headers) as session:
            logger.info(f"📥 Downloading from: {endpoint}")
            logger.info(f"🔑 Using API Key: {API_KEY[:10]}...")
            logger.info(f"📝 Parameters: {params}")
            
            async with session.get(
                endpoint,
                params=params,
                timeout=aiohttp.ClientTimeout(total=600)
            ) as response:
                
                logger.info(f"📡 Response status: {response.status}")
                logger.info(f"📡 Response headers: {dict(response.headers)}")
                
                if response.status == 401:
                    logger.error("❌ Authentication failed: Invalid API Key")
                    return None
                elif response.status == 403:
                    logger.error("❌ Forbidden: API Key expired or no requests remaining")
                    return None
                elif response.status != 200:
                    # Try to read error message
                    try:
                        error_data = await response.json()
                        logger.error(f"❌ API error: {error_data}")
                    except:
                        logger.error(f"❌ Download failed with status: {response.status}")
                    return None
                
                # Get content length if available
                content_length = response.headers.get('Content-Length')
                if content_length:
                    logger.info(f"📊 Expected file size: {int(content_length) / (1024*1024):.2f} MB")
                
                total_size = 0
                with open(file_path, "wb") as f:
                    async for chunk in response.content.iter_chunked(8192):
                        if chunk:
                            f.write(chunk)
                            total_size += len(chunk)
                
                # Verify the download
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    if file_size > 0:
                        file_size_mb = file_size / (1024 * 1024)
                        logger.info(f"✅ Successfully downloaded: {filename} ({file_size_mb:.2f} MB)")
                        
                        # Check content type to ensure we got the right file
                        content_type = response.headers.get('Content-Type', '')
                        if stream_type == "audio" and 'audio' not in content_type.lower():
                            logger.warning(f"⚠️ Unexpected content type for audio: {content_type}")
                        elif stream_type == "video" and 'video' not in content_type.lower():
                            logger.warning(f"⚠️ Unexpected content type for video: {content_type}")
                        
                        return file_path
                    else:
                        logger.error(f"❌ Downloaded file is empty: {filename}")
                        # Try to delete the empty file
                        try:
                            os.remove(file_path)
                        except:
                            pass
                        return None
                else:
                    logger.error(f"❌ File was not created: {filename}")
                    return None
                    
    except asyncio.TimeoutError:
        logger.error(f"⏰ Timeout downloading {video_id}")
        return None
    except aiohttp.ClientError as e:
        logger.error(f"🌐 Network error downloading {video_id}: {e}")
        return None
    except Exception as e:
        logger.error(f"💥 Error downloading {video_id}: {e}")
        return None

async def get_usage_info():
    """Get API key usage information"""
    logger = LOGGER("AloneMusic/platforms/Youtube.py")
    
    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        async with aiohttp.ClientSession(headers=headers) as session:
            status_url = f"{YOUR_API_URL}/api/status"
            
            async with session.get(
                status_url,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"📊 API Status: {data}")
                    return data
                else:
                    logger.error(f"❌ Failed to get API status: {response.status}")
                    return None
                    
    except Exception as e:
        logger.error(f"💥 Error getting API status: {e}")
        return None

async def check_api_key_status():
    """Check if API key is valid and has remaining requests"""
    logger = LOGGER("AloneMusic/platforms/Youtube.py")
    
    usage_info = await get_usage_info()
    
    if not usage_info:
        logger.error("❌ Failed to check API key status")
        return False
    
    remaining = usage_info.get('requests_remaining', 0)
    if remaining <= 0:
        logger.error("❌ API key has no remaining requests")
        return False
    
    logger.info(f"✅ API Key Status: {remaining} requests remaining")
    return True

async def download_song(link: str) -> str:
    logger = LOGGER("AloneMusic/platforms/Youtube.py")
    
    # Start cleanup task if not already running
    await start_cleanup_task()
    
    # Check API key status first
    if not await check_api_key_status():
        logger.error("❌ API Key check failed. Using fallback method directly.")
        return await fallback_download_song(link)
    
    # Extract video ID
    if 'v=' in link:
        video_id = link.split('v=')[-1].split('&')[0]
    elif 'youtu.be/' in link:
        video_id = link.split('youtu.be/')[-1].split('?')[0]
    else:
        video_id = link
    
    logger.info(f"🎵 [AUDIO] Starting download for: {video_id}")

    if not video_id or len(video_id) < 3:
        logger.error(f"❌ [AUDIO] Invalid video ID: {video_id}")
        return None

    # Get video title for logging
    yt_api = YouTubeAPI()
    video_title = await yt_api.title(link)
    
    if not video_title:
        logger.warning(f"⚠️ [AUDIO] Could not fetch video title for: {link}")

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    # Try to download from API
    logger.info(f"🔗 [API] Using direct download method for audio")
    file_path = await download_direct_from_api(video_id, "audio")
    
    if file_path:
        return file_path
    else:
        logger.error(f"❌ [AUDIO] Failed to download from API: {video_id}")
        logger.info("🔄 Switching to fallback method...")
        return await fallback_download_song(link)

async def fallback_download_song(link: str) -> str:
    """Fallback method using yt-dlp directly"""
    logger = LOGGER("AloneMusic/platforms/Youtube.py")
    
    # Extract video ID
    if 'v=' in link:
        video_id = link.split('v=')[-1].split('&')[0]
    elif 'youtu.be/' in link:
        video_id = link.split('youtu.be/')[-1].split('?')[0]
    else:
        video_id = link
    
    logger.info(f"🔄 [FALLBACK AUDIO] Starting fallback download for: {video_id}")
    
    try:
        cookie_file = cookie_txt_file()
        if cookie_file and os.path.exists(cookie_file):
            logger.info(f"🍪 Using cookie file: {cookie_file}")
            
            # Use yt-dlp as fallback
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(DOWNLOAD_DIR, f'{video_id}.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'cookiefile': cookie_file,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=True)
                filename = ydl.prepare_filename(info)
                mp3_file = os.path.splitext(filename)[0] + '.mp3'
                
                if os.path.exists(mp3_file):
                    logger.info(f"✅ [FALLBACK] Successfully downloaded: {mp3_file}")
                    return mp3_file
                else:
                    logger.error(f"❌ [FALLBACK] File not created: {mp3_file}")
                    return None
        else:
            logger.error("❌ [FALLBACK] No cookie file available")
            return None
    except Exception as e:
        logger.error(f"❌ [FALLBACK] Error: {e}")
        return None

async def download_video(link: str) -> str:
    logger = LOGGER("AloneMusic/platforms/Youtube.py")
    
    # Start cleanup task if not already running
    await start_cleanup_task()
    
    # Check API key status first
    if not await check_api_key_status():
        logger.error("❌ API Key check failed. Using fallback method directly.")
        return await fallback_download_video(link)
    
    # Extract video ID
    if 'v=' in link:
        video_id = link.split('v=')[-1].split('&')[0]
    elif 'youtu.be/' in link:
        video_id = link.split('youtu.be/')[-1].split('?')[0]
    else:
        video_id = link
    
    logger.info(f"🎥 [VIDEO] Starting download for: {video_id}")

    if not video_id or len(video_id) < 3:
        logger.error(f"❌ [VIDEO] Invalid video ID: {video_id}")
        return None

    # Get video title for logging
    yt_api = YouTubeAPI()
    video_title = await yt_api.title(link)
    
    if not video_title:
        logger.warning(f"⚠️ [VIDEO] Could not fetch video title for: {link}")

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    # Try to download from API
    logger.info(f"🔗 [API] Using direct download method for video")
    file_path = await download_direct_from_api(video_id, "video")
    
    if file_path:
        return file_path
    else:
        logger.error(f"❌ [VIDEO] Failed to download from API: {video_id}")
        logger.info("🔄 Switching to fallback method...")
        return await fallback_download_video(link)

async def fallback_download_video(link: str) -> str:
    """Fallback method using yt-dlp directly"""
    logger = LOGGER("AloneMusic/platforms/Youtube.py")
    
    # Extract video ID
    if 'v=' in link:
        video_id = link.split('v=')[-1].split('&')[0]
    elif 'youtu.be/' in link:
        video_id = link.split('youtu.be/')[-1].split('?')[0]
    else:
        video_id = link
    
    logger.info(f"🔄 [FALLBACK VIDEO] Starting fallback download for: {video_id}")
    
    try:
        cookie_file = cookie_txt_file()
        if cookie_file and os.path.exists(cookie_file):
            logger.info(f"🍪 Using cookie file: {cookie_file}")
            
            # Use yt-dlp as fallback
            ydl_opts = {
                'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
                'outtmpl': os.path.join(DOWNLOAD_DIR, f'{video_id}.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'cookiefile': cookie_file,
                'merge_output_format': 'mp4',
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=True)
                filename = ydl.prepare_filename(info)
                
                if os.path.exists(filename):
                    logger.info(f"✅ [FALLBACK] Successfully downloaded: {filename}")
                    return filename
                else:
                    logger.error(f"❌ [FALLBACK] File not created: {filename}")
                    return None
        else:
            logger.error("❌ [FALLBACK] No cookie file available")
            return None
    except Exception as e:
        logger.error(f"❌ [FALLBACK] Error: {e}")
        return None

async def check_file_size(link):
    async def get_format_info(link):
        cookie_file = cookie_txt_file()
        if not cookie_file:
            print("No cookies found. Cannot check file size.")
            return None
            
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "--cookies", cookie_file,
            "-J",
            link,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            print(f'Error:\n{stderr.decode()}')
            return None
        return json.loads(stdout.decode())

    def parse_size(formats):
        total_size = 0
        for format in formats:
            if 'filesize' in format:
                total_size += format['filesize']
        return total_size

    info = await get_format_info(link)
    if info is None:
        return None
    
    formats = info.get('formats', [])
    if not formats:
        print("No formats found.")
        return None
    
    total_size = parse_size(formats)
    return total_size

async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz:
        if "unavailable videos are hidden" in (errorz.decode("utf-8")).lower():
            return out.decode("utf-8")
        else:
            return errorz.decode("utf-8")
    return out.decode("utf-8")


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        for message in messages:
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        return text[entity.offset: entity.offset + entity.length]
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
        return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["title"]

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["duration"]

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["thumbnails"][0]["url"].split("?")[0]

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        try:
            downloaded_file = await download_video(link)
            if downloaded_file:
                return 1, downloaded_file
            else:
                return 0, "Video download failed"
        except Exception as e:
            return 0, f"Video download error: {e}"

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        cookie_file = cookie_txt_file()
        if not cookie_file:
            return []
        playlist = await shell_cmd(
            f"yt-dlp -i --get-id --flat-playlist --cookies {cookie_file} --playlist-end {limit} --skip-download {link}"
        )
        try:
            result = [key for key in playlist.split("\n") if key]
        except:
            result = []
        return result

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            vidid = result["id"]
            yturl = result["link"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        track_details = {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }
        return track_details, vidid

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        cookie_file = cookie_txt_file()
        if not cookie_file:
            return [], link
        ytdl_opts = {"quiet": True, "cookiefile": cookie_file}
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        with ydl:
            formats_available = []
            r = ydl.extract_info(link, download=False)
            for format in r["formats"]:
                try:
                    if "dash" not in str(format["format"]).lower():
                        formats_available.append(
                            {
                                "format": format["format"],
                                "filesize": format.get("filesize"),
                                "format_id": format["format_id"],
                                "ext": format["ext"],
                                "format_note": format["format_note"],
                                "yturl": link,
                            }
                        )
                except:
                    continue
        return formats_available, link

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result")
        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
        return title, duration_min, thumbnail, vidid

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        if videoid:
            link = self.base + link

        try:
            if songvideo or songaudio:
                downloaded_file = await download_song(link)
                if downloaded_file:
                    return downloaded_file, True
                else:
                    return None, False
            elif video:
                downloaded_file = await download_video(link)
                if downloaded_file:
                    return downloaded_file, True
                else:
                    return None, False
            else:
                downloaded_file = await download_song(link)
                if downloaded_file:
                    return downloaded_file, True
                else:
                    return None, False
        except Exception as e:
            print(f"Download failed: {e}")
            return None, False

# Initialize cleanup when module is imported
async def initialize_module():
    """Initialize the module with cleanup task"""
    await start_cleanup_task()

# Start cleanup task when module loads
