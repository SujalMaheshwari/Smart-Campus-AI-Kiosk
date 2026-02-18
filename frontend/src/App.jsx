import { useEffect, useRef, useState } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import Avatar from "./Avatar";
import "./App.css";
import CampusMap from "./Map";
import { LOCATIONS } from "./locations";

function App() {
  const recognitionRef = useRef(null);
  const audioRef = useRef(null);
  const isSpeakingRef = useRef(false);

  const [listening, setListening] = useState(false);
  const [loading, setLoading] = useState(false);
  const [userText, setUserText] = useState(""); 
  const [jsonUrl, setJsonUrl] = useState(null);
  const [caption, setCaption] = useState(""); 
  const [displayedText, setDisplayedText] = useState(""); 
  
  const [activeLocation, setActiveLocation] = useState(null);

  // 👇 GENERIC SUGGESTIONS (No 'UIT' or 'RGPV')
  const allSuggestions = [
    "📅 Exam Schedule", "📚 Download Syllabus", "🔑 Student Login",
    "📞 Contact Registrar", "📍 Where is Library?", "📍 Route to Engineering Block",
    "📍 Where is Admin?", "🎓 Results Date", "🚍 Bus Routes"
  ];

  const [currentSuggestions, setCurrentSuggestions] = useState([]);

  useEffect(() => {
    shuffleSuggestions();
  }, []);

  const shuffleSuggestions = () => {
    const shuffled = [...allSuggestions].sort(() => 0.5 - Math.random());
    setCurrentSuggestions(shuffled.slice(0, 4));
  };

  useEffect(() => {
    // 👇 GENERIC WELCOME MESSAGE
    const welcomeMsg = "Hello! I am your Smart Campus Assistant. Ask me about routes, hostels, or schedules.";
    setCaption(welcomeMsg);
    
    const timestamp = new Date().getTime();

    const audioPath = `http://localhost:8000/audio/welcome.mp3?t=${timestamp}`;
    const jsonPath = `http://localhost:8000/audio/welcome.json?t=${timestamp}`;
    setJsonUrl(jsonPath);
    
    if (!audioRef.current) audioRef.current = new Audio();
    audioRef.current.src = audioPath;
    audioRef.current.oncanplaythrough = () => {
        audioRef.current.play().catch(e => console.log("Click on screen to enable audio"));
    };
  }, []);

  const playTTS = async (text, actionUrl = null, mapTarget = null) => {
    if (!text) return;
    isSpeakingRef.current = true;

    try {
      const res = await fetch("http://localhost:8000/tts-eleven", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });

      const data = await res.json();
      if (!audioRef.current) audioRef.current = new Audio();

      setJsonUrl(data.json_url);
      audioRef.current.src = data.audio_url;
      audioRef.current.load();

      audioRef.current.onplay = () => {
        setCaption(text); 
      };

      audioRef.current.onended = () => {
        isSpeakingRef.current = false;
        
        if (mapTarget && LOCATIONS[mapTarget]) {
            setActiveLocation(LOCATIONS[mapTarget]);
        }

        if (actionUrl) {
            setTimeout(() => window.open(actionUrl, "_blank"), 1000); 
        }
      };

      audioRef.current.oncanplaythrough = () => {
          audioRef.current.play().catch(e => console.log("Autoplay blocked"));
      };

    } catch (err) {
      isSpeakingRef.current = false;
      console.error("TTS error:", err);
    }
  };

  const sendToBackend = async (text) => {
    if (!text || !text.trim()) return; 
    setUserText(text); 
    setLoading(true); 

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      const data = await res.json();

      setLoading(false);

      if (data.reply) {
          playTTS(data.reply, data.action_url, data.map_target);
      } 

    } catch (error) {
      console.error("Backend Error:", error);
      setLoading(false);
      setCaption("Error connecting to Server.");
    }
  };

  const handleSuggestionClick = (text) => {
    sendToBackend(text);
    setTimeout(() => { shuffleSuggestions(); }, 500);
  };

  useEffect(() => {
    setDisplayedText(""); 
    if (!caption) return;
    let index = 0;
    const intervalId = setInterval(() => {
      index++;
      setDisplayedText(caption.slice(0, index));
      if (index >= caption.length) clearInterval(intervalId);
    }, 25);
    return () => clearInterval(intervalId);
  }, [caption]);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.lang = "en-US";
      recognition.continuous = false; 
      recognition.onstart = () => setListening(true);
      recognition.onend = () => setListening(false);
      recognition.onresult = (e) => {
        const text = e.results[0][0].transcript;
        sendToBackend(text);
      };
      recognitionRef.current = recognition;
    }
  }, []);

  return (
    <div className="app-container">
      <Canvas camera={{ position: [0, 1.2, 1.8], fov: 30 }}>
        <ambientLight intensity={0.9} />
        <directionalLight position={[2, 4, 2]} intensity={1.2} />
        <Avatar audioRef={audioRef} jsonUrl={jsonUrl} />
        <OrbitControls enableZoom={false} enablePan={false} target={[0, 0.9, 0]} />
      </Canvas>

      {/* 👇 GENERIC BRANDING SECTION */}
      <div className="rgpv-branding">
        {/* Logo hata kar Generic Icon laga diya */}
        <div style={{ fontSize: "50px", marginBottom: "10px", filter: "drop-shadow(0 0 5px rgba(255,255,255,0.5))" }}>
            🎓
        </div>
        <div className="rgpv-title">
          <h1>Smart Campus AI</h1>
          <p>Interactive Kiosk System</p>
        </div>
      </div>

      {userText && (
        <div className="user-bubble">
          <span className="user-label">You Asked:</span>
          <p className="user-text">"{userText}"</p>
        </div>
      )}

      {loading && (
        <div className="loading-indicator">
           <span className="dot">🔍</span> Processing Request...
        </div>
      )}

      {activeLocation && (
        <CampusMap 
          targetLocation={activeLocation} 
          onClose={() => setActiveLocation(null)} 
        />
      )}

      {!activeLocation && !loading && (
        <div className="suggestions-container">
           <p className="suggestion-title">✨ Try asking:</p>
           <div className="chips-grid">
             {currentSuggestions.map((s, i) => (
               <button key={i} className="chip-btn" onClick={() => handleSuggestionClick(s)}>
                 {s}
               </button>
             ))}
           </div>
        </div>
      )}

      {displayedText && (
        <div className="caption-box">
          <p style={{ margin: 0 }}>
            {displayedText}
            <span className="cursor">|</span> 
          </p>
        </div>
      )}

      <div className="controls-bar">
        <input 
          type="text" 
          placeholder="Ask (e.g., Where is Library?)" 
          className="chat-input"
          onKeyDown={(e) => {
            if (e.key === "Enter" && e.target.value) {
              sendToBackend(e.target.value);
              e.target.value = "";
            }
          }}
        />
        <div className="separator"></div>
        <button
          onClick={() => recognitionRef.current?.start()}
          disabled={listening}
          className={`mic-button ${listening ? "listening" : ""}`}
        >
          {listening ? "🛑" : "🎙️"}
        </button>
      </div>
    </div>
  );
}

export default App;