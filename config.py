import re
from os import getenv
from dotenv import load_dotenv
from pyrogram import filters
import os
load_dotenv()

API_ID = 23212132
API_HASH = "1c17efa86bdef8f806ed70e81b473c20"
BOT_TOKEN = "8581475111:AAGvWCB17nrAvy9031m3cqmdD350SeFJ8H0"
OWNER_USERNAME = "@Spotifywave"
BOT_USERNAME = "@Shizuku_robot"
BOT_NAME = "Shizuku"
ASSUSERNAME = "@ShadowBotAssistant"
EVALOP = list(map(int, getenv("EVALOP", "").split()))
MONGO_DB_URI = getenv("MONGO_DB_URI", "mongodb+srv://fosownerzoro_db_user:fosownerzoro_db_user@cluster0.sgmzbvx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
LOGGER_ID = -1002800777153
DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 36000))
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
VIDEO_API_URL = os.getenv("VIDEO_API_URL", "http://127.0.0.1:8000")
API_KEY = os.getenv("API_KEY", "e3f2b1e27e97409fb2f2d70f6442fb29")

GPT_API = getenv("GPT_API", None)
DEEP_API = getenv("DEEP_API", None)
OWNER_ID = 8429156335

HEROKU_APP_NAME = None
HEROKU_API_KEY = None
UPSTREAM_REPO = getenv("UPSTREAM_REPO", "t.me/spotifywave")
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "Master")
GIT_TOKEN = getenv("GIT_TOKEN", "")

SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/ShadowBOtsHQ")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/ShadowBotsSupport")

AUTO_LEAVING_ASSISTANT = bool(getenv("AUTO_LEAVING_ASSISTANT", True))
AUTO_LEAVE_ASSISTANT_TIME = int(getenv("ASSISTANT_LEAVE_TIME", "3600"))
SERVER_PLAYLIST_LIMIT = int(getenv("SERVER_PLAYLIST_LIMIT", "3000"))
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", "2500"))
SONG_DOWNLOAD_DURATION = int(getenv("SONG_DOWNLOAD_DURATION", "9999999"))
SONG_DOWNLOAD_DURATION_LIMIT = int(getenv("SONG_DOWNLOAD_DURATION_LIMIT", "9999999"))

SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "22b6125bfe224587b722d6815002db2b")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "c9c63c6fbf2f467c8bc68624851e9773")
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", "5242880000"))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", "5242880000"))

STRING1 = getenv("STRING_SESSION" ,"BQG8AHcARrMsnSYij7yTk209tBma95rskuFV9JccDI7_xHxRGT59be7W9uzRlk6dLSWi2qQiSHoy-yR6nGcEDMUF2a7r2rT-YTwrn_nSzZwevYU6wtIOzmKNuJfi3v-IFH7YqLYKTOJ8Gvrw2Fa1JpL1OGEyl6oCjteTr9BIt9sabcq6LewYIAo5VTcRtujXpzLODBvTRxkPO0ZsP24ZAHkmNTCcqAm1nIMGArBdeuh-3-b80OVI2CjrUpUsLA8JTlV1TCc6tNjDk5zxfe9cHqlWBoyYwv-MFiYX1bHPFk8XrrH4YO7RIu9SJ8grGjOFyDbxAPFS4t9d6B1ylFF8SrSlBnKJvQAAAAFIn-xqAA") 
STRING2 = getenv("STRING_SESSION2", None)
STRING2 = getenv("STRING_SESSION2", None)
STRING3 = getenv("STRING_SESSION3", None)
STRING4 = getenv("STRING_SESSION4", None)
STRING5 = getenv("STRING_SESSION5", None)


AYU = [
    "💞", "🦋", "🔍", "🧪", "🦋", "⚡️", "🔥", "🦋", "🎩", "🌈", "🍷", "🥂", "🦋", "🥃", "🥤", "🕊️",
    "🦋", "🦋", "🕊️", "🦋", "🕊️", "🦋", "🦋", "🦋", "🪄", "💌", "🦋", "🦋", "🧨"
]

AYUV = [ "<b>нєу</b> {0}, 💗\n\n๏ ᴛʜɪs ɪs {1} !\n\n➻ {1} ɪs ʏᴏᴜʀ ᴘᴇʀsᴏɴᴀʟ ᴍᴜsɪᴄ ᴄᴏᴍᴘᴀɴɪᴏɴ, ʜᴇʀᴇ ᴛᴏ ʙʀɪɴɢ ʜᴀʀᴍᴏɴʏ ᴛᴏ ʏᴏᴜʀ ᴅᴀʏ. EɴJᴏʏ sᴇᴀᴍʟᴇss ᴍᴜsɪᴄ ᴘʟᴀʏʙᴀᴄᴋ, ᴄᴜʀᴀᴛᴇᴅ ᴘʟᴀʏʟɪsᴛs, ᴀɴᴅ ᴇғғᴏʀᴛʟᴇss ᴄᴏɴᴛʀᴏʟ, ᴀʟʟ ᴀᴛ ʏᴏᴜʀ ғɪɴɢᴇʀᴛɪᴘs. Lᴇᴛ {1} ᴇʟᴇᴠᴀᴛᴇ ʏᴏᴜʀ ʟɪsᴛᴇɴɪɴɢ ᴇxᴘᴇʀɪᴇɴᴄᴇ ᴡɪᴛʜ ᴇᴀsᴇ ᴀɴᴅ sᴛʏʟᴇ.\n\n<b><u>Sᴜᴘᴘᴏʀᴛᴇᴅ Pʟᴀᴛғᴏʀᴍs :</b></u> ʏᴏᴜᴛᴜʙᴇ, sᴘᴏᴛɪғʏ, ʀᴇssᴏ, ᴀᴘᴘʟᴇ ᴍᴜsɪᴄ ᴀɴᴅ sᴏᴜɴᴅᴄʟᴏᴜᴅ.\n──────────────────\n<b>๏ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʜᴇʟᴩ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴍʏ ᴍᴏᴅᴜʟᴇs ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅs🦋.</b> "  ,
]

BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}

START_IMG_URL = getenv(
    "START_IMG_URL", "https://files.catbox.moe/9orx6x.jpg"
)
PING_IMG_URL = getenv(
    "PING_IMG_URL", "https://files.catbox.moe/410ebd.jpg"
)
PLAYLIST_IMG_URL = "https://files.catbox.moe/hqhh0n.jpg"
STATS_IMG_URL = "https://files.catbox.moe/hqhh0n.jpg"
TELEGRAM_AUDIO_URL = "https://files.catbox.moe/5ni0on.jpg"
TELEGRAM_VID_URL = "https://files.catbox.moe/5ni0on.jpg"
STREAM_IMG_URL = "https://files.catbox.moe/5ni0on.jpg"
SOUNCLOUD_IMG_URL = "https://files.catbox.moe/5ni0on.jpg"
YOUTUBE_IMG_URL = "https://files.catbox.moe/5ni0on.jpg"
SPOTIFY_ARTIST_IMG_URL = "https://files.catbox.moe/5ni0on.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://files.catbox.moe/5ni0on.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://files.catbox.moe/5ni0on.jpg"
STATS_VID_URL = "https://files.catbox.moe/diotfk.mp4"

def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))

DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))

if SUPPORT_CHANNEL:
    if not re.match("(?:http|https)://", SUPPORT_CHANNEL):
        raise SystemExit(
            "[ERROR] - Your SUPPORT_CHANNEL url is wrong. Please ensure that it starts with https://"
        )

if SUPPORT_CHAT:
    if not re.match("(?:http|https)://", SUPPORT_CHAT):
        raise SystemExit(
            "[ERROR] - Your SUPPORT_CHAT url is wrong. Please ensure that it starts with https://"
)
