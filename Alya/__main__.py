import asyncio
import importlib
import signal
import sys
from Alya.platforms.Youtube import initialize_module
from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from Alya import LOGGER, app, userbot
from Alya.core.call import alya
from Alya.misc import sudo
from Alya.plugins import ALL_MODULES
from Alya.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS


async def shutdown(signal, loop):
    """Cleanup tasks tied to the service's shutdown."""
    LOGGER("Alya").info(f"Received exit signal {signal.name}...")
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    LOGGER("Alya").info(f"Cancelling {len(tasks)} outstanding tasks")
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()


async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("Assistant session not filled, please fill a Pyrogram session...")
        exit()
    await sudo()
    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except:
        pass
    await app.start()
    for all_module in ALL_MODULES:
        importlib.import_module("Alya.plugins" + all_module)
    LOGGER("Alya.plugins").info("Annie's modules loaded...")
    await userbot.start()
    await alya.start()
    try:
        await alya.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
    except NoActiveGroupCall:
        LOGGER("Alya").error(
            "Please turn on the voice chat of your log group/channel.\n\nAnnie Bot stopped..."
        )
        exit()
    except:
        pass
    await alya.decorators()
    LOGGER("Alya").info("Annie Started Successfully...")
    await idle()
    await app.stop()  
    await initialize_module()
    await userbot.stop()
    LOGGER("Alya").info("Stopping Annie Bot ...")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    
    # Register signal handlers
    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, lambda s=s: asyncio.create_task(shutdown(s, loop))
        )
    
    try:
        loop.run_until_complete(init())
    finally:
        loop.close()
