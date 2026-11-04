import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
import yt_dlp

# GitHub Secrets se credentials uthana
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

if not API_ID or not API_HASH or not SESSION_STRING:
    print("Error: API_ID, API_HASH, or SESSION_STRING is missing in environment variables/secrets!")
    exit(1)

# Pyrogram Client Setup (Userbot session string ke sath)
app = Client(
    "music_bot",
    api_id=int(API_ID),
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

# PyTgCalls Setup
call_py = PyTgCalls(app)

# /start command
@app.on_message(filters.command("start"))
async def start_handler(client: Client, message: Message):
    await message.reply_text(
        "👋 **Hello! Main aapka Telegram Voice Chat Music Bot hoon.**\n\n"
        "Commands:\n"
        "• `/play [YouTube Link / Song Name]` - Voice chat me music play karne ke liye\n"
        "• `/pause` - Music pause karne ke liye\n"
        "• `/resume` - Music resume karne ke liye\n"
        "• `/stop` - Voice chat band karne ke liye\n"
        "• `/volume [1-200]` - Volume set karne ke liye"
    )

# /play command (YouTube links & Search support)
@app.on_message(filters.command("play"))
async def play_handler(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("⚠️ Kripya koi YouTube link ya song name dein! Example: `/play Faded`")
        return

    query = " ".join(message.command[1:])
    chat_id = message.chat.id
    m = await message.reply_text("🔍 **Searching & Processing audio...**")

    try:
        # yt-dlp options se direct audio stream URL nikalna
        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
        }
        
        if query.startswith("http"):
            search_query = query
        else:
            search_query = f"ytsearch:{query}"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=False)
            if "entries" in info:
                info = info["entries"][0]
            
            stream_url = info.get("url")
            title = info.get("title", "Unknown Title")

        await m.edit_text(f"🎵 **Playing:** `{title}`")
        
        # PyTgCalls ke zariye Voice Chat me audio stream play karna
        await call_py.join_group_call(
            chat_id,
            AudioPiped(stream_url)
        )
    except Exception as e:
        await m.edit_text(f"❌ Error aa gaya: `{e}`")

# /pause command
@app.on_message(filters.command("pause"))
async def pause_handler(client: Client, message: Message):
    try:
        await call_py.pause_stream(message.chat.id)
        await message.reply_text("⏸ **Music Paused.**")
    except Exception as e:
        await message.reply_text(f"❌ Error: `{e}`")

# /resume command
@app.on_message(filters.command("resume"))
async def resume_handler(client: Client, message: Message):
    try:
        await call_py.resume_stream(message.chat.id)
        await message.reply_text("▶️ **Music Resumed.**")
    except Exception as e:
        await message.reply_text(f"❌ Error: `{e}`")

# /stop command
@app.on_message(filters.command("stop"))
async def stop_handler(client: Client, message: Message):
    try:
        await call_py.leave_group_call(message.chat.id)
        await message.reply_text("⏹ **Stopped and Left Voice Chat.**")
    except Exception as e:
        await message.reply_text(f"❌ Error: `{e}`")

# /volume command
@app.on_message(filters.command("volume"))
async def volume_handler(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("⚠️ Usage: `/volume 100` (1 se 200 tak)")
        return
    try:
        vol = int(message.command[1])
        if 1 <= vol <= 200:
            await call_py.change_volume_call(message.chat.id, vol)
            await message.reply_text(f"🔊 **Volume set to {vol}%**")
        else:
            await message.reply_text("⚠️ Volume 1 aur 200 ke beech honi chahiye!")
    except Exception as e:
        await message.reply_text(f"❌ Error: `{e}`")

async def main():
    print("Starting Pyrogram Client & PyTgCalls...")
    await app.start()
    await call_py.start()
    print("Bot is running successfully!")
    # Bot ko chalu rakhne ke liye idle loop
    await asyncio.gather(
        asyncio.Event().wait()
    )

if __name__ == "__main__":
    asyncio.run(main())
