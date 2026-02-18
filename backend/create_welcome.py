import asyncio
import edge_tts
import os
import subprocess

# 👇 GENERIC TEXT
TEXT = "Hello! I am your Smart Campus Assistant. Ask me about routes, hostels, or schedules."
VOICE = "en-IN-NeerjaNeural"

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "audio")

def get_executable_path(filename, subfolder=None):
    """File ko dhoondne ke liye helper function"""
    # 1. Check inside specific subfolder (e.g., backend/rhubarb/rhubarb.exe)
    if subfolder:
        sub_path = os.path.join(BASE_DIR, subfolder, filename)
        if os.path.exists(sub_path): return sub_path
    
    # 2. Check in current folder (e.g., backend/rhubarb.exe)
    root_path = os.path.join(BASE_DIR, filename)
    if os.path.exists(root_path): return root_path
    
    # 3. Assume it's in System PATH
    return filename

async def generate_welcome():
    if not os.path.exists(AUDIO_DIR):
        os.makedirs(AUDIO_DIR)

    mp3_path = os.path.join(AUDIO_DIR, "welcome.mp3")
    wav_path = os.path.join(AUDIO_DIR, "welcome.wav")
    json_path = os.path.join(AUDIO_DIR, "welcome.json")

    print(f"🎤 Generating Welcome Audio...")

    # 1. Generate MP3
    communicate = edge_tts.Communicate(TEXT, VOICE)
    await communicate.save(mp3_path)
    print(f"✅ MP3 Saved.")

    # 2. Find Tools (FFmpeg & Rhubarb)
    ffmpeg_cmd = get_executable_path("ffmpeg.exe")
    rhubarb_cmd = get_executable_path("rhubarb.exe", "rhubarb") # 👈 Yeh folder ke andar bhi dhoondega

    # Debug Prints
    print(f"🛠️ Using FFmpeg: {ffmpeg_cmd}")
    print(f"🛠️ Using Rhubarb: {rhubarb_cmd}")

    # 3. Convert to WAV
    print("🔄 Converting to WAV...")
    try:
        subprocess.run([ffmpeg_cmd, "-y", "-i", mp3_path, "-ac", "1", "-ar", "16000", wav_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print("❌ Error: 'ffmpeg.exe' nahi mila! Please ensure ffmpeg.exe backend folder mein hai.")
        return

    # 4. Generate Lip Sync
    print("👄 Generating Lip Sync Data...")
    try:
        subprocess.run([rhubarb_cmd, "-f", "json", "-o", json_path, wav_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✅ JSON Saved.")
    except FileNotFoundError:
        print("❌ Error: 'rhubarb.exe' nahi mila! Please ensure backend/rhubarb folder exist karta hai.")
        return
    except subprocess.CalledProcessError:
        print("❌ Error: Rhubarb crash ho gaya. Check karo WAV file sahi bani hai kya.")
        return

    # Cleanup
    if os.path.exists(wav_path):
        os.remove(wav_path)
        
    print("\n🎉 Success! Welcome message update ho gaya.")

if __name__ == "__main__":
    asyncio.run(generate_welcome())