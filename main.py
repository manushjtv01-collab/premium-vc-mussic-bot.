
import os
from pyrogram import Client, filters
from pytgcalls import PyTgCalls

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION = os.environ["SESSION_STRING"]

app = Client(
    "PremiumMusic",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION
)

call = PyTgCalls(app)


@app.on_message(filters.command("start"))
async def start(_, message):
    await message.reply_text(
        "👑 PREMIUM VC MUSIC BOT\n\n"
        "/play AUDIO_URL\n"
        "/pause\n"
        "/resume\n"
        "/skip\n"
        "/stop\n"
        "/volume 50"
    )


@app.on_message(filters.command("play"))
async def play(_, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "Usage: /play AUDIO_URL"
        )

    url = message.text.split(None, 1)[1]

    try:
        await call.play(message.chat.id, url)
        await message.reply_text("🎵 Music Started!")
    except Exception as e:
        await message.reply_text(f"Error: {e}")


@app.on_message(filters.command("pause"))
async def pause(_, message):
    await call.pause(message.chat.id)
    await message.reply_text("⏸ Paused!")


@app.on_message(filters.command("resume"))
async def resume(_, message):
    await call.resume(message.chat.id)
    await message.reply_text("▶️ Resumed!")


@app.on_message(filters.command("skip"))
async def skip(_, message):
    await call.leave_call(message.chat.id)
    await message.reply_text("⏭ Skipped!")


@app.on_message(filters.command("stop"))
async def stop(_, message):
    await call.leave_call(message.chat.id)
    await message.reply_text("⏹ Stopped!")


@app.on_message(filters.command("volume"))
async def volume(_, message):
    try:
        value = int(message.command[1])
        if not 1 <= value <= 200:
            raise ValueError

        await call.change_volume_call(
            message.chat.id, value
        )
        await message.reply_text(
            f"🔊 Volume: {value}%"
        )
    except (ValueError, IndexError):
        await message.reply_text(
            "Use /volume 1-200"
        )


call.run()
