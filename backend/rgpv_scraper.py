import requests
import io
import os
import re
import urllib3
from pypdf import PdfReader
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image

# SSL Warning Disable
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# 1. CONFIGURATION
# ==========================================

PYTESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

if os.path.exists(PYTESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = PYTESSERACT_PATH
else:
    print(f"⚠️ Warning: Tesseract not found at {PYTESSERACT_PATH}. OCR might fail.")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Referer": "https://www.rgpv.ac.in/",
    "Connection": "keep-alive"
}

# ==========================================
# 2. GOVERNANCE MODULE (UNCHANGED)
# ==========================================

DIRECT_URLS = {
    "registrar": "https://www.rgpv.ac.in/AboutRGTU/Registrar.aspx",
    "vice chancellor": "https://www.rgpv.ac.in/AboutRGTU/ViceChancellor.aspx",
    "vc": "https://www.rgpv.ac.in/AboutRGTU/ViceChancellor.aspx",
    "chancellor": "https://www.rgpv.ac.in/AboutRGTU/Chancellor.aspx",
    "director": "https://www.rgpv.ac.in/AboutRGTU/ListOfDirectors.aspx", 
    "list of directors": "https://www.rgpv.ac.in/AboutRGTU/ListOfDirectors.aspx",
    "exam controller": "https://www.rgpv.ac.in/AboutRGTU/ControllerOfExamination.aspx",
    "controller of examination": "https://www.rgpv.ac.in/AboutRGTU/ControllerOfExamination.aspx",
    "finance": "https://www.rgpv.ac.in/AboutRGTU/FinanceCommittee.aspx",
    "women grievance": "https://www.rgpv.ac.in/AboutRGTU/WomenGrievanceCell.aspx",
    "anti-ragging": "https://www.rgpv.ac.in/AboutRGTU/AntiRagging.aspx"
}

def fetch_and_clean_page(url):
    try:
        session = requests.Session()
        session.get("https://www.rgpv.ac.in/", headers=HEADERS, verify=False, timeout=10)
        response = session.get(url, headers=HEADERS, verify=False, timeout=15)
        
        if response.status_code != 200: return None
        soup = BeautifulSoup(response.content, "html.parser")
        
        if "can not found" in soup.get_text().lower() or "404" in soup.title.string if soup.title else False:
            return None

        for tag in soup(["script", "style", "header", "footer", "nav", "aside"]): tag.decompose()
        for div in soup.find_all("div", class_=["menu", "navigation", "top-bar", "sidebar"]): div.decompose()

        main_content = soup.find(id="ctl00_ContentPlaceHolder1_pnlContents")
        text = main_content.get_text() if main_content else soup.get_text()
        
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        return '\n'.join(chunk for chunk in chunks if chunk)[:4000]
    except Exception:
        return None

def scrape_official_profile(role_name):
    print(f"🏛️ Deep Scraping RGPV Website for: '{role_name}'...")
    final_text = None
    used_url = None

    if role_name in DIRECT_URLS:
        url = DIRECT_URLS[role_name]
        print(f"🔗 Trying Direct Link: {url}")
        final_text = fetch_and_clean_page(url)
        if final_text:
            used_url = url
            print("✅ Direct Link worked!")

    if not final_text:
        print("🌍 Searching Google/DDG...")
        query = f"site:rgpv.ac.in {role_name} profile"
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=3))
                for res in results:
                    test_url = res['href']
                    final_text = fetch_and_clean_page(test_url)
                    if final_text:
                        used_url = test_url
                        print("✅ Search Link worked!")
                        break
        except Exception: pass

    if not final_text: return "Could not find the official page."
    return f"OFFICIAL SOURCE: {used_url}\nPAGE DATA:\n{final_text}"


# ==========================================
# 3. NOTICE BOARD & OCR MODULE (DUAL SOURCE 🔥)
# ==========================================

def get_live_notices(keyword=None):
    """
    Combines notices from Homepage & Archive.
    Ignores 'javascript:' links AND General Menu Links.
    """
    print(f"🕵️‍♂️ Scraping Notices (Keyword: {keyword})...")
    
    session = requests.Session()
    notices = []
    seen_urls = set()

    # 🛑 BLACKLIST: In words wale links ko notice mat samjho
    IGNORED_URLS = [
        "aboutrgtu", "login", "gallery", "contact", "examination.aspx", 
        "result.aspx", "download.aspx", "alumini", "placement", "scheme", 
        "syllabus", "academic", "javascript", "dopostback", "#"
    ]

    # Helper function to validate link
    def is_valid_notice(text, href):
        href_lower = href.lower()
        
        # 1. Text Length Check (Chhote links menu items hote hain)
        if len(text) < 15: return False 
        
        # 2. Blacklist Check
        if any(bad in href_lower for bad in IGNORED_URLS): return False
        
        # 3. Valid Types Check
        if ".pdf" in href_lower or "notice" in href_lower or "view" in href_lower or "click here" in text.lower():
            return True
            
        return False

    # --- SOURCE 1: HOMEPAGE ---
    try:
        home_url = "https://www.rgpv.ac.in/"
        resp_home = session.get(home_url, headers=HEADERS, verify=False, timeout=10)
        soup_home = BeautifulSoup(resp_home.content, "html.parser")
        
        for link in soup_home.find_all('a', href=True):
            text = link.text.strip()
            href = link['href']
            
            if is_valid_notice(text, href):
                full_url = href if href.startswith('http') else f"https://www.rgpv.ac.in/{href}"
                full_url = full_url.replace("//", "/").replace("https:/", "https://")
                
                if full_url not in seen_urls:
                    notice_obj = {"date": "Latest Alert", "title": text, "url": full_url}
                    
                    # Keyword Check (Strict)
                    if keyword:
                        # Sirf tab add karo agar keyword title mein ho
                        if keyword.lower() in text.lower():
                            notices.append(notice_obj)
                            seen_urls.add(full_url)
                    else:
                        notices.append(notice_obj)
                        seen_urls.add(full_url)
    except Exception: pass

    # --- SOURCE 2: ARCHIVE PAGE ---
    try:
        archive_url = "https://www.rgpv.ac.in/Uni/ImpNoticeArchive.aspx"
        resp_arch = session.get(archive_url, headers=HEADERS, verify=False, timeout=10)
        soup_arch = BeautifulSoup(resp_arch.content, "html.parser")
        
        for row in soup_arch.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) >= 2:
                col1_text = cols[0].text.strip() # Date
                col2 = cols[1] # Title + Link
                
                if re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', col1_text):
                    date = col1_text
                    title = col2.text.strip()
                    link_tag = col2.find("a")
                    
                    if link_tag and 'href' in link_tag.attrs:
                        link = link_tag['href']
                        if is_valid_notice(title, link):
                            if not link.startswith("http"): link = "https://www.rgpv.ac.in" + link
                            
                            if link not in seen_urls:
                                notice_obj = {"date": date, "title": title, "url": link}
                                
                                if keyword:
                                    if keyword.lower() in title.lower():
                                        notices.append(notice_obj)
                                        seen_urls.add(link)
                                else:
                                    notices.append(notice_obj)
                                    seen_urls.add(link)
    except Exception: pass

    print(f"✅ Total Found: {len(notices)} notices.")
    return notices[:5]

def extract_text_from_pdf(pdf_url):
    print(f"📄 Downloading PDF: {pdf_url}")
    
    # 1. Bad Link Check
    if "javascript" in pdf_url.lower() or "underconstruction" in pdf_url.lower():
        return "[ERROR: The link is broken or under construction on the RGPV website.]"

    try:
        # 2. Header Check (Kya ye sach mein PDF hai?)
        response = requests.get(pdf_url, headers=HEADERS, verify=False, timeout=15)
        content_type = response.headers.get("Content-Type", "").lower()
        
        if "text/html" in content_type:
            return "[ALERT: This is a webpage, not a PDF. Please view the link directly.]"

        pdf_bytes = response.content
        f = io.BytesIO(pdf_bytes)
        
        text = ""
        
        # 3. PyPDF Extraction
        try:
            reader = PdfReader(f)
            max_pages = min(3, len(reader.pages))
            for i in range(max_pages):
                extracted = reader.pages[i].extract_text()
                if extracted: text += extracted + "\n"
        except: pass

        # 4. OCR Extraction (Fallback)
        if len(text.strip()) < 50:
            print("⚠️ Switching to OCR Mode...")
            try:
                # Poppler Path Optional (Agar Environment Variable set hai)
                images = convert_from_bytes(pdf_bytes, first_page=1, last_page=2, poppler_path=None)
                ocr_text = ""
                for img in images:
                    ocr_text += pytesseract.image_to_string(img) + "\n"
                
                if ocr_text.strip(): text = f"[OCR SUCCESS]\n{ocr_text}"
                else: text = "[OCR FAILED]"
            except Exception as e:
                print(f"❌ OCR Error: {e}")
                text = "[SCANNED DOCUMENT: Unable to read image text.]"
        
        return text[:4000]

    except Exception as e:
        print(f"⚠️ PDF Error: {e}")
        return "Could not download PDF."

# ==========================================
# 4. GENERIC SEARCH
# ==========================================
def perform_web_search(search_query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(search_query, max_results=5))
            return "\n".join([f"Title: {r['title']}\nSnippet: {r['body']}" for r in results])
    except: return "Search failed."