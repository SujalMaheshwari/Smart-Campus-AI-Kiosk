import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Polyline, useMap } from "react-leaflet";
import QRCode from "react-qr-code"; 
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { KIOSK_LOCATION } from "./locations";

// --- ICONS (Wohi purane wale) ---
const startIcon = new L.Icon({
    iconUrl: 'https://cdn-icons-png.flaticon.com/512/684/684908.png',
    iconSize: [35, 35],
    iconAnchor: [17, 35]
});

const endIcon = new L.Icon({
    iconUrl: 'https://cdn-icons-png.flaticon.com/512/854/854878.png',
    iconSize: [35, 35],
    iconAnchor: [5, 35]
});

const movingIcon = new L.DivIcon({
  html: "<div style='width:12px;height:12px;background:blue;border-radius:50%;border:2px solid white;box-shadow:0 0 8px blue;'></div>",
  className: "",
  iconSize: [12, 12]
});

function ChangeView({ coords }) {
  const map = useMap();
  map.setView(coords, 17);
  return null;
}

const CampusMap = ({ targetLocation, onClose }) => {
  const [currentStep, setCurrentStep] = useState(0); 
  const [googleMapsLink, setGoogleMapsLink] = useState("");

  const generatePath = (start, end) => {
    const steps = 100;
    const path = [];
    for (let i = 0; i <= steps; i++) {
      const lat = start[0] + (end[0] - start[0]) * (i / steps);
      const lng = start[1] + (end[1] - start[1]) * (i / steps);
      path.push([lat, lng]);
    }
    return path;
  };

  const animationPath = generatePath(KIOSK_LOCATION, targetLocation.coords);

  useEffect(() => {
    const link = `https://www.google.com/maps/dir/?api=1&origin=${KIOSK_LOCATION[0]},${KIOSK_LOCATION[1]}&destination=${targetLocation.coords[0]},${targetLocation.coords[1]}&travelmode=walking`;
    setGoogleMapsLink(link);

    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev + 1) % animationPath.length);
    }, 50); 

    return () => clearInterval(interval);
  }, [targetLocation]);

  return (
    <div className="map-overlay">
      <div className="map-card-container">
        
        {/* ❌ CLOSE BUTTON (Top Right Corner) */}
        <button onClick={onClose} className="close-btn" title="Close Map">✖</button>

        {/* 🗺️ MAP SECTION (Top Half) */}
        <div className="map-section">
          <MapContainer center={KIOSK_LOCATION} zoom={17} style={{ height: "100%", width: "100%" }}>
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            <ChangeView coords={targetLocation.coords} />
            <Marker position={KIOSK_LOCATION} icon={startIcon} />
            <Marker position={targetLocation.coords} icon={endIcon} />
            <Polyline positions={[KIOSK_LOCATION, targetLocation.coords]} color="#3388ff" weight={5} dashArray="10, 10" />
            <Marker position={animationPath[currentStep]} icon={movingIcon} />
          </MapContainer>
        </div>

        {/* ℹ️ INFO SECTION (Bottom Half) */}
        <div className="info-section">
          <h3 style={{ margin: "0 0 10px 0", color: "#333" }}>📍 {targetLocation.name}</h3>
          
          {/* QR CODE - Ab nahi katega */}
          <div className="qr-box">
            <QRCode value={googleMapsLink} size={140} />
          </div>
          <p style={{ fontSize: "14px", color: "#666", margin: "5px 0 15px 0" }}>
            📱 Scan to navigate on phone
          </p>

          <div style={{ textAlign: "left", width: "100%", paddingLeft: "10px" }}>
            <h4 style={{ margin: "0 0 5px 0" }}>👣 Steps:</h4>
            <ul style={{ paddingLeft: "20px", margin: 0, fontSize: "14px" }}>
              {targetLocation.steps.map((step, i) => (
                <li key={i} style={{ marginBottom: "4px" }}>{step}</li>
              ))}
            </ul>
          </div>
        </div>

      </div>
    </div>
  );
};

export default CampusMap;