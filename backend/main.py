import os
import uuid
import json
import requests
import subprocess
import time
import asyncio
import numpy as np
import pypdf
import faiss
from sentence_transformers import SentenceTransformer
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import edge_tts 
import re 
from rgpv_scraper import perform_web_search, get_live_notices, extract_text_from_pdf, scrape_official_profile

# IMPORTS FOR BUS & HOSTEL
from bus_data import search_bus
from hostel_data import search_hostel

app = FastAPI()

CHAT_HISTORY = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
DATA_DIR = os.path.join(BASE_DIR, "data")
JSON_FILE = os.path.join(BASE_DIR, "faqs.json")

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")
VOICE_ID = "en-IN-NeerjaNeural" 

class RAGEngine:
    def __init__(self):
        print("🧠 Initializing Smart Campus AI Brain...") # Generic Print
        self.documents = []
        self.model = None
        self.index = None
        self.load_json()
        self.load_documents()
        if self.documents:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            embeddings = self.model.encode(self.documents, convert_to_numpy=True).astype('float32')
            d = embeddings.shape[1] 
            self.index = faiss.IndexFlatL2(d) 
            self.index.add(embeddings)
    def load_json(self):
        if os.path.exists(JSON_FILE):
            try:
                with open(JSON_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        self.documents.append(f"[Source: FAQ] Q: {item['question']} A: {item['answer']}")
            except: pass
    def load_documents(self):
        if not os.path.exists(DATA_DIR): return
        for filename in os.listdir(DATA_DIR):
            path = os.path.join(DATA_DIR, filename)
            if filename.endswith(".txt"):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        text = f.read()
                        if text.strip(): self.documents.append(text)
                except: pass
    def retrieve(self, query: str, k: int = 3) -> List[str]:
        if not self.index or not query: return []
        query_embedding = self.model.encode(query, convert_to_numpy=True).astype('float32').reshape(1, -1)
        D, I = self.index.search(query_embedding, k)
        return [self.documents[i] for i in I[0] if i < len(self.documents)]

rag_engine = RAGEngine()

class ChatRequest(BaseModel):
    text: str

class TTSRequest(BaseModel):
    text: str

def get_executable_path(filename, subfolder=None):
    if subfolder:
        local_path = os.path.join(BASE_DIR, subfolder, filename)
        if os.path.exists(local_path): return local_path
    root_path = os.path.join(BASE_DIR, filename)
    if os.path.exists(root_path): return root_path
    return filename

def cleanup_old_files():
    try:
        current_time = time.time()
        for filename in os.listdir(AUDIO_DIR):
            file_path = os.path.join(AUDIO_DIR, filename)
            if filename.startswith("welcome"): continue 
            if os.path.isfile(file_path) and (current_time - os.path.getmtime(file_path) > 300):
                os.remove(file_path)
    except Exception as e: pass

@app.post("/tts-eleven")
async def tts_handler(req: TTSRequest):
    cleanup_old_files()
    file_id = str(uuid.uuid4())
    mp3_filename = f"{file_id}.mp3"
    mp3_filepath = os.path.join(AUDIO_DIR, mp3_filename)
    
    try:
        clean_text = re.sub(r'\(?https?://\S+\)?', '', req.text)
        communicate = edge_tts.Communicate(clean_text, VOICE_ID)
        await communicate.save(mp3_filepath)
        
        wav_filepath = os.path.join(AUDIO_DIR, f"{file_id}.wav")
        json_filepath = os.path.join(AUDIO_DIR, f"{file_id}.json")
        
        ffmpeg_cmd = get_executable_path("ffmpeg.exe")
        rhubarb_cmd = get_executable_path("rhubarb.exe", "rhubarb")

        subprocess.run([ffmpeg_cmd, "-y", "-i", mp3_filepath, "-ac", "1", "-ar", "16000", wav_filepath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run([rhubarb_cmd, "-f", "json", "-o", json_filepath, wav_filepath], capture_output=True)

        return {
            "audio_url": f"http://localhost:8000/audio/{mp3_filename}",
            "json_url": f"http://localhost:8000/audio/{f'{file_id}.json'}"
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def root():
    return {"status": "Smart Campus AI Backend Running"}

SMART_LINKS = {
    "login": "https://rgpv.ac.in/Login/StudentLogin.aspx",
    "portal": "https://rgpv.ac.in/Login/StudentLogin.aspx",
    "result": "http://result.rgpv.ac.in/Result/ProgramSelect.aspx",
    "time table": "https://rgpv.ac.in/Uni/frm_ViewScheme.aspx",
    "syllabus": "https://rgpv.ac.in/Uni/frm_ViewScheme.aspx",
    "calendar": "https://www.rgpv.ac.in/Academics/frm_AcademicCalender.aspx"
}

@app.post("/chat")
def chat(req: ChatRequest):
    global CHAT_HISTORY
    if len(CHAT_HISTORY) > 4: CHAT_HISTORY = CHAT_HISTORY[-4:]
        
    print(f"\n🗣️ USER: '{req.text}'")
    query_lower = req.text.lower()
    
    system_data = ""
    action_url = None
    map_target = None 

    # 1. Smart Links
    for key, url in SMART_LINKS.items():
        if key in query_lower: return {"reply": "Opening link...", "action_url": url}

    # 2. Location Map (Includes Bus & Hostels)
    locations_map = {
        "library": ["library", "books", "reading room"],
        "uit": ["uit", "engineering", "college block"],
        "admin": ["admin", "administrative", "registrar office"],
        "canteen": ["canteen", "food", "cafeteria"],
        "bus stop": ["bus stop", "bus stand"],
        "hostel": ["hostel", "boys hostel", "accommodation"], 
        "girls hostel": ["girls hostel", "ladies hostel"]
    }

    # Flags
    is_map_query = any(x in query_lower for x in ["where is", "route to", "location of", "way to", "go to", "map"])
    is_bus_query = any(x in query_lower for x in ["bus", "driver", "transport", "gaadi", "route"]) 
    is_hostel_query = any(x in query_lower for x in ["hostel", "warden", "fees", "mess", "room", "accommodation"])
    is_notice_query = any(x in query_lower for x in ["notice", "news", "circular", "update", "date", "form", "schedule"])
    is_governance_query = any(x in query_lower for x in ["chancellor", "vc", "registrar", "director", "dean", "hod"])

    mode = "general"

    # --- DECISION LOGIC ---

    # A. MAP MODE 🗺️
    if is_map_query:
        print("⚡ Mode: Navigation / Map")
        mode = "map"
        for key, keywords in locations_map.items():
            if any(k in query_lower for k in keywords):
                map_target = key
                system_data = f"User is asking for directions to {key.upper()}. I am opening the map on the screen."
                break
        
        if not map_target:
            if "bus" in query_lower: mode = "bus_fallback"
            elif "hostel" in query_lower: mode = "hostel_fallback"

    # B. BUS INFO MODE 🚌
    if is_bus_query and (mode != "map" or mode == "bus_fallback"):
        print("⚡ Mode: Bus Transport Info")
        mode = "bus"
        found_buses = search_bus(query_lower)
        if found_buses:
            system_data = "FOUND BUS DETAILS:\n"
            for b in found_buses:
                system_data += f"Route {b['route_no']} to {b['destination']}.\n"
                system_data += f"Driver: {b['driver']} (Ph: {b['phone']}).\n"
                system_data += f"Stops: {', '.join(b['stops'])}.\n\n"
        else:
            system_data = "User asked for bus info, but no specific matching route found. Available routes go to: Bairagarh, MP Nagar, New Market, Ayodhya Bypass, Kolar."

    # C. HOSTEL INFO MODE 🏠
    elif is_hostel_query and (mode != "map" or mode == "hostel_fallback"):
        print("⚡ Mode: Hostel Info")
        mode = "hostel"
        
        search_result = search_hostel(query_lower)
        found_hostels = search_result["hostels"]
        extra_info = search_result["extra_info"]
        
        system_data = ""

        if "mess_timings" in extra_info:
            m = extra_info["mess_timings"]
            system_data += f"🍽️ MESS TIMINGS:\nBreakfast: {m['breakfast']}\nLunch: {m['lunch']}\nDinner: {m['dinner']}\nSunday Special: {m['sunday_special']}\n\n"

        if "rules" in extra_info:
            system_data += f"📜 HOSTEL RULES:\n"
            for rule in extra_info["rules"]:
                system_data += f"- {rule}\n"
            system_data += "\n"

        if found_hostels:
            system_data += "🏠 FOUND HOSTELS:\n"
            for h in found_hostels:
                system_data += f"Name: {h['name']}\nWarden: {h['warden']} (Ph: {h['phone']})\nFees: {h['fees']}\nFacilities: {', '.join(h['facilities'])}\n\n"
        
        if not system_data:
            system_data = "User asked for hostel info. Available hostels: Bhaskaracharya, Chandrashekhar Azad, APJ Abdul Kalam, CV Raman (Boys); Maharani Laxmi Bai, Rani Ahilya Bai (Girls)."

    # D. NOTICE MODE 📰
    elif is_notice_query:
        print("⚡ Mode: Live Notices")
        mode = "notice"
        stop_words = ["any", "notice", "about", "regarding", "the", "for", "of", "rgpv", "university", "date", "change", "download", "link"]
        words = query_lower.split()
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        search_keyword = keywords[0] if keywords else None
        
        if "exam" in query_lower: search_keyword = "exam"
        if "result" in query_lower: search_keyword = "result"

        notices = get_live_notices(search_keyword)
        if notices:
            top = notices[0]
            print(f"📄 Reading PDF for Notice: {top['title']}")
            pdf_text = extract_text_from_pdf(top['url'])
            system_data = f"LATEST NOTICE:\nTitle: {top['title']}\nDate: {top['date']}\nLink: {top['url']}\nCONTENT:\n{pdf_text[:3000]}"
            action_url = top['url']
        else:
            system_data = f"No recent notices found for '{search_keyword}'."

    # E. GOVERNANCE MODE 🏛️
    elif is_governance_query:
        print("⚡ Mode: Governance Scraping")
        mode = "official"
        role_asked = "official"
        system_data = scrape_official_profile(role_asked)

    # F. GENERIC/RAG 📚
    elif mode == "general":
        print("📚 Mode: Local Knowledge Base")
        mode = "rag"
        docs = rag_engine.retrieve(req.text)
        system_data = "\n".join(docs)

    # --- PROMPT SETTING (GENERIC) ---
    base_instructions = ""
    if mode == "map":
        base_instructions = "Tell the user 'Here is the route to [Location]. You can scan the QR code for directions.' Keep it short."
    elif mode == "bus":
        base_instructions = "Provide the Bus Route Number, Driver Name, and Contact Number clearly."
    elif mode == "hostel":
        base_instructions = "Provide Hostel Name, Warden Contact, Fees, and Type (Boys/Girls) clearly."
    elif mode == "notice":
        base_instructions = "Summarize the notice. Enclose links in brackets: (url)."
    else:
        base_instructions = "Answer concisely. Enclose links in brackets."

    # 👇 UPDATED GENERIC PROMPT
    prompt = f"""You are a Smart Campus AI Assistant designed for Universities.
    Be helpful, professional, and concise.
    
    CONTEXT DATA (Use this to answer):
    {system_data}
    
    USER QUESTION: {req.text}
    
    INSTRUCTIONS:
    {base_instructions}
    
    IMPORTANT GUIDELINES:
    - Do NOT mention specific university names (like 'RGPV') unless explicitly asked by the user.
    - Refer to the campus simply as 'The University' or 'The Campus'.
    - If explaining a route, use generic terms like 'the academic block' or 'the main library'.
    
    Reply in English.
    """

    try:
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        res = requests.post(f"{ollama_host}/api/generate", json={
            "model": "llama3", "prompt": prompt, "stream": False, "options": {"num_ctx": 4096}
        })
        reply = res.json().get("response", "").strip()
        CHAT_HISTORY.append({"user": req.text, "ai": reply})
        return {"reply": reply, "action_url": action_url, "map_target": map_target}
    except Exception as e:
        return {"reply": "Error connecting to brain.", "action_url": None}