import os
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream


# =========================
# TELEGRAM CREDENTIALS
# =========================

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION = os.environ["SESSION_STRING"]


# =========================
# CLIENT SETUP
# =========================

app = Client(
    "PremiumMusic",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION
)

call = PyTgCalls(app)


# =========================
# START COMMAND
# =========================

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


# =========================
# PLAY MP3 COMMAND
# =========================

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

        file_path = os.path.join(
            "downloads",
            f"{message.chat.id}_{replied.id}.mp3"
        )

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
