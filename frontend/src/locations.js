export const KIOSK_LOCATION = [23.3093, 77.3619]; 

export const LOCATIONS = {
  "library": {
    name: "RGPV Central Library",
    coords: [23.3120, 77.3610], 
    steps: ["Go straight from Main Gate", "Pass the UIT Building", "Library is the round building on right"]
  },
  "admin": {
    name: "Administrative Block",
    coords: [23.3080, 77.3620],
    steps: ["Walk straight 200m", "Red building on your right is Admin Block"]
  },
  "uit": {
    name: "UIT RGPV (College)",
    coords: [23.3105, 77.3630],
    steps: ["Take the left road", "The large academic block is UIT"]
  },
  "canteen": {
    name: "University Canteen",
    coords: [23.3100, 77.3625],
    steps: ["Located near the UIT Parking area"]
  },
  "bus stop": {
    name: "University Bus Stop",
    coords: [23.3135, 77.3605], 
    steps: ["Exit the Main Building", "Walk towards the Sports Ground", "Bus Stop is located behind the UIT Parking area"]
  },
  
  // 🏠 BOYS HOSTEL ZONE (All 4 Hostels are here)
  "hostel": { 
    name: "Boys Hostel Zone",
    coords: [23.3145, 77.3585], // Near Sports Complex
    steps: ["Go past the Library", "Cross the Sports Ground", "Bhaskaracharya & APJ Kalam Hostels are here"]
  },

  // 🏠 GIRLS HOSTEL ZONE (Both Hostels are here)
  "girls hostel": { 
    name: "Girls Hostel Zone",
    coords: [23.3065, 77.3640], // Near UIT/Polytechnic
    steps: ["Take the road towards Polytechnic Wing", "Girls Hostels (Ahilya Bai & Laxmi Bai) are on the left"]
  }
};