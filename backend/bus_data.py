# backend/bus_data.py

BUS_ROUTES = [
    {
        "route_no": "1",
        "destination": "Bairagarh",
        "driver": "Ramesh Kumar",
        "phone": "98765-43210",
        "stops": ["Lal Ghati", "Halalpura", "Bairagarh Chichali", "Sehore Naka"]
    },
    {
        "route_no": "2",
        "destination": "MP Nagar",
        "driver": "Suresh Singh",
        "phone": "91234-56789",
        "stops": ["Chetak Bridge", "Jyoti Talkies", "Board Office", "DB Mall"]
    },
    {
        "route_no": "3",
        "destination": "New Market",
        "driver": "Manoj Yadav",
        "phone": "99887-76655",
        "stops": ["Polytechnic Square", "Kamla Park", "Roshanpura", "TT Nagar"]
    },
    {
        "route_no": "4",
        "destination": "Ayodhya Bypass",
        "driver": "Vikram Patel",
        "phone": "88990-01122",
        "stops": ["Minal Residency", "JK Road", "Bhanpur", "Karond"]
    },
    {
        "route_no": "5",
        "destination": "Kolar Road",
        "driver": "Deepak Sharma",
        "phone": "77665-54433",
        "stops": ["Chuna Bhatti", "Sarvdharm", "Bima Kunje", "Mandakini"]
    }
]

def search_bus(query):
    query = query.lower()
    results = []
    
    for bus in BUS_ROUTES:
        # Check Route No, Destination, or Stops
        if (bus["route_no"] in query) or \
           (bus["destination"].lower() in query) or \
           any(stop.lower() in query for stop in bus["stops"]):
            results.append(bus)
            
    return results