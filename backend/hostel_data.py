# backend/hostel_data.py

HOSTEL_DATA = [
    # --- BOYS HOSTELS ---
    {
        "name": "Bhaskaracharya Boys Hostel",
        "type": "Boys",
        "warden": "Chief Warden Office",
        "phone": "0755-2678870",
        "fees": "₹12,000 per semester (approx)",
        "capacity": "90 Seats",
        "facilities": ["Wi-Fi", "Mess", "24x7 Power", "Hot Water"]
    },
    {
        "name": "Chandrashekhar Azad Boys Hostel",
        "type": "Boys",
        "warden": "Chief Warden Office",
        "phone": "0755-2678870",
        "fees": "₹12,000 per semester (approx)",
        "capacity": "276 Seats",
        "facilities": ["Basketball Court", "Common Room", "RO Water"]
    },
    {
        "name": "A.P.J. Abdul Kalam Boys Hostel",
        "type": "Boys",
        "warden": "Chief Warden Office",
        "phone": "0755-2678870",
        "fees": "₹12,000 per semester (approx)",
        "capacity": "358 Seats",
        "facilities": ["Newest Building", "Lifts", "Study Hall"]
    },
    
    # --- GIRLS HOSTELS ---
    {
        "name": "Maharani Laxmi Bai Girls Hostel",
        "type": "Girls",
        "warden": "Matron / Warden",
        "phone": "0755-2678812",
        "fees": "₹12,000 per semester (approx)",
        "capacity": "422 Seats",
        "facilities": ["Single/Double Rooms", "Separate Mess", "Guest Room"]
    },
    {
        "name": "Rani Ahilya Bai Girls Hostel",
        "type": "Girls",
        "warden": "Matron / Warden",
        "phone": "0755-2678812",
        "fees": "₹12,000 per semester (approx)",
        "capacity": "328 Seats",
        "facilities": ["Two-Seater Rooms", "Basketball Court", "TV Room"]
    }
]

# 🕒 MESS TIMINGS & MENU
MESS_INFO = {
    "breakfast": "08:00 AM - 09:30 AM (Poha, Paratha, Samosa, Tea)",
    "lunch": "01:00 PM - 02:00 PM (Dal, Rice, Roti, Seasonal Veg)",
    "tea": "05:30 PM - 06:00 PM (Tea & Snacks/Biscuits)",
    "dinner": "08:00 PM - 09:30 PM (Dal, Roti, Rice, Sabji)",
    "sunday_special": "Sunday Lunch: Puri, Sabji, Pulao, Sweet (Gulab Jamun/Kheer)"
}

# 📜 HOSTEL RULES
HOSTEL_RULES = [
    "✅ Attendance: Mandatory biometric/register attendance every night.",
    "⏰ Curfew (Boys): Entry allowed till 9:00 PM.",
    "⏰ Curfew (Girls): Entry allowed till 8:30 PM.",
    "🚫 Prohibitions: Alcohol, Smoking, and Ragging are strictly prohibited.",
    "📝 Leave: Written permission from Warden is required for night outs.",
    "🔇 Noise: Silence hours must be maintained after 10:30 PM."
]

def search_hostel(query):
    query = query.lower()
    results = []
    
    # 1. Search for specific hostels
    for hostel in HOSTEL_DATA:
        if (hostel["name"].lower() in query) or \
           (hostel["type"].lower() in query and "hostel" in query):
            results.append(hostel)

    # 2. Check for Rules or Timings
    extra_info = {}
    
    # Mess/Food Query
    if any(x in query for x in ["food", "mess", "lunch", "dinner", "breakfast", "tea", "menu", "eat"]):
        extra_info["mess_timings"] = MESS_INFO
        
    # Rules/Timing Query
    if any(x in query for x in ["rule", "time", "curfew", "allowed", "gate", "late"]):
        extra_info["rules"] = HOSTEL_RULES

    return {"hostels": results, "extra_info": extra_info}