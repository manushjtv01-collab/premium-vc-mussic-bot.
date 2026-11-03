import os
import asyncio
import yt_dlp

from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream


# Telegram Credentials
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION = os.environ["SESSION_STRING"]


# Bot Setup
app = Client(
    "PremiumMusic",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION
)

call = PyTgCalls(app)


# Start Command
@app.on_message(filters.command("start"))
async def start(_, message):
    await message.reply_text(
        "🎵 PREMIUM VC MUSIC BOT\n\n"
        "/play song name or YouTube link\n"
        "/pause - Pause music\n"
        "/resume - Resume music\n"
        "/skip - Skip music\n"
        "/stop - Stop music\n"
        "/volume 50 - Change volume"
    )


# Search and Play
@app.on_message(filters.command("play"))
async def play(_, message):

    if len(message.command) < 2:
        return await message.reply_text(
            "Usage: /play song name or YouTube link"
        )

    query = " ".join(message.command[1:])

    status = await message.reply_text("🔎 Searching song...")

    def get_audio():
        options = {
            "format": "bestaudio/best",
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True
        }

        with yt_dlp.YoutubeDL(options) as ydl:

            if query.startswith(("http://", "https://")):
                info = ydl.extract_info(query, download=False)
            else:
                result = ydl.extract_info(
                    f"ytsearch1:{query}",
                    download=False
                )
                info = result["entries"][0]

            return info["url"], info.get("title", "Unknown")

    try:
        url, title = await asyncio.to_thread(get_audio)

        await call.play(
            message.chat.id,
            MediaStream(url)
        )

        await status.edit_text(
            f"🎵 Now Playing:\n{title}"
        )

    except Exception as e:
        await status.edit_text(f"❌ Error: {e}")


# Pause Command
@app.on_message(filters.command("pause"))
async def pause(_, message):
    try:
        await call.pause(message.chat.id)
        await message.reply_text("⏸ Music Paused!")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")


# Resume Command
@app.on_message(filters.command("resume"))
async def resume(_, message):
    try:
        await call.resume(message.chat.id)
        await message.reply_text("▶️ Music Resumed!")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")


# Skip Command
@app.on_message(filters.command("skip"))
async def skip(_, message):
    try:
        await call.leave_call(message.chat.id)
        await message.reply_text("⏭ Music Skipped!")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")


# Stop Command
@app.on_message(filters.command("stop"))
async def stop(_, message):
    try:
        await call.leave_call(message.chat.id)
        await message.reply_text("⏹ Music Stopped!")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")


# Volume Command
@app.on_message(filters.command("volume"))
async def volume(_, message):
    try:
        if len(message.command) < 2:
            return await message.reply_text(
                "Usage: /volume 1-200"
            )

        value = int(message.command[1])

        if not 1 <= value <= 200:
            return await message.reply_text(
                "Volume must be between 1 and 200."
            )

        await call.change_volume_call(
            message.chat.id,
            value
        )

        await message.reply_text(
            f"🔊 Volume: {value}%"
        )

    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")


# Run Bot
call.run()
