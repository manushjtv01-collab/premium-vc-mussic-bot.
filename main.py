import os
import asyncio
from pyrofork import Client, filters
from pyrofork.types import Message
from pytgcalls import PyTgCalls, idle
from pytgcalls.types.input_stream import AudioPiped
import yt_dlp

# Environment variables from GitHub Secrets
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSION_STRING = os.getenv("SESSION_STRING", "")

if not API_ID or not API_HASH or not SESSION_STRING:
    print("Error: API_ID, API_HASH, and SESSION_STRING must be set!")
    exit(1)

# Initialize Pyrofork Client
app = Client(
    "music_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

# Initialize PyTgCalls v3
call_py = PyTgCalls(app)
active_calls = set()

@app.on_message(filters.command("start"))
async def start_cmd(client: Client, message: Message):
    await message.reply_text(
        "👋 **Hello! I am your Telegram Voice Chat Music Bot.**\n\n"
        "**Commands:**\n"
        "• `/play [YouTube Link / Song Name / Reply to Audio]` - Play music in voice chat\n"
        "• `/pause` - Pause music\n"
        "• `/resume` - Resume music\n"
        "• `/stop` - Stop music and leave VC\n"
        "• `/volume [1-200]` - Adjust volume"
    )

def download_audio(query: str) -> str:
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
    }
    
    if not query.startswith("http"):
        query = f"ytsearch:{query}"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        if 'entries' in info:
            info = info['entries'][0]
        file_path = ydl.prepare_filename(info)
        file_path = os.path.splitext(file_path)[0] + ".mp3"
        return file_path

@app.on_message(filters.command("play") & filters.group)
async def play_cmd(client: Client, message: Message):
    chat_id = message.chat.id
    
    # Check if replied to an audio file
    if message.reply_to_message and (message.reply_to_message.audio or message.reply_to_message.document):
        m = await message.reply_text("📥 Downloading audio file...")
        file_path = await message.reply_to_message.download(file_name="downloads/")
        await m.edit("🎵 Joining Voice Chat and playing...")
        try:
            await call_py.join_group_call(
                chat_id,
                AudioPiped(file_path)
            )
            active_calls.add(chat_id)
            await m.edit("▶️ **Playing audio file in Voice Chat!**")
        except Exception as e:
            await m.edit(f"❌ Error: {str(e)}")
        return

    if len(message.command) < 2:
        await message.reply_text("❌ Please provide a YouTube link, song name, or reply to an audio file!")
        return

    query = message.text.split(None, 1)[1]
    m = await message.reply_text(f"🔍 Searching & Downloading: `{query}`...")

    try:
        loop = asyncio.get_event_loop()
        file_path = await loop.run_in_executor(None, download_audio, query)
        
        await m.edit("🎵 Joining Voice Chat and streaming...")
        await call_py.join_group_call(
            chat_id,
            AudioPiped(file_path)
        )
        active_calls.add(chat_id)
        await m.edit(f"▶️ **Now Playing:** `{query}`")
    except Exception as e:
        await m.edit(f"❌ Error: {str(e)}")

@app.on_message(filters.command("pause") & filters.group)
async def pause_cmd(client: Client, message: Message):
    chat_id = message.chat.id
    try:
        await call_py.pause_stream(chat_id)
        await message.reply_text("⏸ **Paused the music.**")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@app.on_message(filters.command("resume") & filters.group)
async def resume_cmd(client: Client, message: Message):
    chat_id = message.chat.id
    try:
        await call_py.resume_stream(chat_id)
        await message.reply_text("▶️ **Resumed the music.**")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@app.on_message(filters.command("stop") & filters.group)
async def stop_cmd(client: Client, message: Message):
    chat_id = message.chat.id
    try:
        await call_py.leave_group_call(chat_id)
        active_calls.discard(chat_id)
        await message.reply_text("⏹ **Stopped and left the Voice Chat.**")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@app.on_message(filters.command("volume") & filters.group)
async def volume_cmd(client: Client, message: Message):
    chat_id = message.chat.id
    if len(message.command) < 2:
        await message.reply_text("❌ Please specify volume level (1 to 200). Example: `/volume 100`")
        return
    try:
        volume = int(message.command[1])
        if volume < 1 or volume > 200:
            await message.reply_text("❌ Volume must be between 1 and 200.")
            return
        await call_py.change_volume_call(chat_id, volume)
        await message.reply_text(f"🔊 **Volume set to:** `{volume}%`")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

async def main():
    os.makedirs("downloads", exist_ok=True)
    print("Starting Pyrofork Client...")
    await app.start()
    print("Starting PyTgCalls...")
    await call_py.start()
    print("Music Bot is Online and Running!")
    await idle()
    await app.stop()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
