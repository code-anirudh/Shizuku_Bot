from Alya.core.bot import alya
from Alya.core.dir import dirr
from Alya.core.git import git
from Alya.core.userbot import Userbot
from Alya.misc import dbb, heroku
from Alya.server import start_flask
from .logging import LOGGER

dirr()
git()
dbb()
heroku()

start_flask()

app = alya()
userbot = Userbot()

from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()
