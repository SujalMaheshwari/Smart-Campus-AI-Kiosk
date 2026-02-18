# 🎓 Smart Campus AI Kiosk

**An Interactive, Voice-Activated 3D Assistant for University Campuses.**

This project is a next-generation Kiosk system designed to help students and visitors navigate large campuses. It features a **real-time 3D Avatar**, **Voice Interaction**, and **Dynamic Map Navigation**.

![Project Screenshot](frontend/public/images/rgpvcampus.png) 
*(Note: Replace the image path above with a screenshot of your actual UI)*

---

## 🌟 Key Features

* **🗣️ Voice-Activated AI:** Speak naturally to the assistant to ask questions.
* **🤖 3D Interactive Avatar:** Features a realistic 3D avatar with **real-time lip-sync** (powered by Rhubarb & EdgeTTS).
* **🗺️ Visual Navigation:** dynamically generates paths to key locations (Library, Hostels, Admin Block) and displays them on an interactive map.
* **📱 QR Handoff:** Generates QR codes for users to transfer directions to their mobile phones.
* **🚌 Utility Services:** Provides real-time bus schedules, driver contacts, and hostel fee structures.
* **⚡ Fast & Responsive:** Built with Vite and FastAPI for low-latency performance.

---

## 🛠️ Tech Stack

### **Frontend**
* **React.js (Vite):** Core framework.
* **React Three Fiber (R3F):** For rendering the 3D Avatar.
* **Tailwind CSS / Custom CSS:** For the futuristic UI.
* **Leaflet Maps:** For the campus map overlay.

### **Backend**
* **Python (FastAPI):** High-performance backend API.
* **Edge TTS:** For high-quality neural voice generation.
* **Rhubarb Lip Sync:** For generating accurate mouth shapes (visemes).
* **RAG (Retrieval-Augmented Generation):** Custom engine to fetch notices and static data.

---

## 🚀 Installation & Setup

Since this project uses heavy audio processing tools, please follow the steps below carefully.

### **1. Clone the Repository**
```bash
git clone [https://github.com/YourUsername/Smart-Campus-AI-Kiosk.git](https://github.com/YourUsername/Smart-Campus-AI-Kiosk.git)
cd Smart-Campus-AI-Kiosk