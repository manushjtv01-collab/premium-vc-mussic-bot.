import os
import asyncio

from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream


# Telegram Credentials
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION = os.environ["SESSION_STRING"]


# Client Setup
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
        "MP3 file par reply karke /play bhejo.\n\n"
        "/pause - Pause music\n"
        "/resume - Resume music\n"
        "/stop - Stop music\n"
        "/volume 50 - Change volume"
    )


# Play Telegram MP3
@app.on_message(filters.command("play"))
async def play(_, message):

    replied = message.reply_to_message

    if not replied:
        return await message.reply_text(
            "❌ MP3 file par reply karke /play bhejo."
        )

    audio = replied.audio
    document = replied.document

    if audio:
        filename = audio.file_name or "music.mp3"

    elif document and (
        document.mime_type == "audio/mpeg"
        or (document.file_name or "").lower().endswith(".mp3")
    ):
        filename = document.file_name or "music.mp3"

    else:
        return await message.reply_text(
            "❌ Please reply to an MP3 file."
        )

    status = await message.reply_text(
        "⏳ Downloading MP3..."
    )

    try:
        os.makedirs("downloads", exist_ok=True)

        safe_name = f"{message.chat.id}_{replied.id}.mp3"
        file_path = os.path.join("downloads", safe_name)

        downloaded = await replied.download(
            file_name=file_path
        )

        if not downloaded:
            return await status.edit_text(
                "❌ MP3 download failed."
            )

        await call.play(
            message.chat.id,
            MediaStream(downloaded)
        )

        await status.edit_text(
            f"🎵 Playing: {filename}"
        )

    except Exception as e:
        await status.edit_text(
            f"❌ Error: {str(e)}"
        )


# Pause
@app.on_message(filters.command("pause"))
async def pause(_, message):
    try:
        await call.pause(message.chat.id)
        await message.reply_text("⏸ Music Paused!")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")


# Resume
@app.on_message(filters.command("resume"))
async def resume(_, message):
    try:
        await call.resume(message.chat.id)
        await message.reply_text("▶️ Music Resumed!")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")


# Stop
@app.on_message(filters.command("stop"))
async def stop(_, message):
    try:
        await call.leave_call(message.chat.id)
        await message.reply_text("⏹ Music Stopped!")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")


# Volume
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
                "Volume 1 se 
