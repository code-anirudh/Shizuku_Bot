from motor.motor_asyncio import AsyncIOMotorClient

from config import MONGO_DB_URI

from ..logging import LOGGER

LOGGER(__name__).info("ᴄᴏɴɴᴇᴄᴛɪɴɢ ᴛᴏ ʏᴏᴜʀ ᴍᴏɴɢᴏ ᴅᴀᴛᴀʙᴀsᴇ...")
try:
    _mongo_async_ = AsyncIOMotorClient(MONGO_DB_URI)
    mongodb = _mongo_async_.Anon
    LOGGER(__name__).info("ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴛᴏ ʏᴏᴜʀ ᴍᴏɴɢᴏ ᴅᴀᴛᴀʙᴀsᴇ.")
except:
    LOGGER(__name__).error("Failed to connect to your Mongo Database.")
    exit()
