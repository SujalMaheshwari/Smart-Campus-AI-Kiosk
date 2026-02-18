import { useGLTF } from "@react-three/drei";
import { useEffect, useRef, useState } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

// --- CONFIGURATION ---
const SMOOTHING_SPEED = 0.2; // 0.1 to 0.5 (Higher = snappier)
const TEETH_OPEN_Y = -0.02;  // How far DOWN the teeth move (in meters)
const TEETH_OPEN_Z = 0.01;   // Push teeth forward slightly (optional)
const TEETH_ROT_X = 0.2;     // How much the teeth ROTATE (radians)

const visemeMapping = {
  A: "viseme_PP", B: "viseme_kk", C: "viseme_I", D: "viseme_aa",
  E: "viseme_O", F: "viseme_U", G: "viseme_FF", H: "viseme_nn",
  X: "viseme_sil",
};

// Map vowels to how much the teeth should drop (0.0 to 1.0)
const jawTargetMapping = {
  A: 0.0,   // Closed
  B: 0.3,   // Slight
  C: 0.4,   // Medium
  D: 1.0,   // AA - MAX OPEN
  E: 0.6,   // O - Open
  F: 0.3,   // U - Narrow
  G: 0.1,   // F
  H: 0.3,   // L
  X: 0.0,   // Closed
};

export default function Avatar({ audioRef, jsonUrl }) {
  const group = useRef();
  const { scene } = useGLTF("/models/avatar.glb");

  const faceMeshRef = useRef(null);
  const teethMeshRef = useRef(null);
  const [lipSyncData, setLipSyncData] = useState(null);

  // Store initial teeth position to allow resetting
  const initialTeethPos = useRef({ x:0, y:0, z:0 });
  const initialTeethRot = useRef({ x:0, y:0, z:0 });

  useEffect(() => {
    if (group.current) {
      group.current.position.set(0, -1, 0);
      group.current.scale.set(1.3, 1.3, 1.3);
    }
  }, []);

  /* FIND MESHES */
  useEffect(() => {
    scene.traverse((obj) => {
      if (obj.name === "Wolf3D_Head" || obj.name === "Wolf3D_Avatar") {
        faceMeshRef.current = obj;
      }
      if (obj.name === "Wolf3D_Teeth") {
        teethMeshRef.current = obj;
        // Save original position so we don't lose it
        initialTeethPos.current = obj.position.clone();
        initialTeethRot.current = obj.rotation.clone();
        
        // HACK: Sometimes SkinnedMeshes ignore manual position. 
        // We set this to false to allow manual override if needed (rarely).
        obj.matrixAutoUpdate = true; 
        console.log("🦷 Teeth Mesh Found & Unlocked");
      }
    });
  }, [scene]);

  useEffect(() => {
    if (!jsonUrl) return;
    fetch(jsonUrl)
      .then(res => res.json())
      .then(data => setLipSyncData(data))
      .catch(err => console.error("❌ LipSync Error:", err));
  }, [jsonUrl]);

  useFrame((state, delta) => {
    if (!faceMeshRef.current || !lipSyncData || !audioRef.current) return;

    const t = audioRef.current.currentTime;
    const cues = lipSyncData.mouthCues;
    const cue = cues.find((c) => t >= c.start && t <= c.end);
    
    // 1. Determine Target Intensity (0.0 to 1.0)
    let targetIntensity = 0;
    let currentViseme = "X";

    if (cue && !audioRef.current.paused && !audioRef.current.ended) {
      currentViseme = cue.value;
      targetIntensity = jawTargetMapping[cue.value] || 0;
    }

    // --- 2. ANIMATE FACE (Morph Targets) ---
    const dict = faceMeshRef.current.morphTargetDictionary;
    const influences = faceMeshRef.current.morphTargetInfluences;

    // Reset morphs
    Object.values(visemeMapping).forEach((v) => {
      if (dict[v] !== undefined) influences[dict[v]] = 0;
    });

    // Apply active morph
    const visemeName = visemeMapping[currentViseme];
    if (dict[visemeName] !== undefined) {
      // Smoothly interpolate for less jitter
      const currentVal = influences[dict[visemeName]];
      influences[dict[visemeName]] = THREE.MathUtils.lerp(currentVal, 1, SMOOTHING_SPEED);
    }

    // --- 3. ANIMATE TEETH (Manual Position Override) ---
    if (teethMeshRef.current) {
      const teeth = teethMeshRef.current;

      // Calculate TARGET position based on intensity
      // We start at initialPos and subtract/add based on intensity
      const targetY = initialTeethPos.current.y + (TEETH_OPEN_Y * targetIntensity);
      const targetZ = initialTeethPos.current.z + (TEETH_OPEN_Z * targetIntensity);
      const targetRotX = initialTeethRot.current.x + (TEETH_ROT_X * targetIntensity);

      // Smoothly Move
      teeth.position.y = THREE.MathUtils.lerp(teeth.position.y, targetY, SMOOTHING_SPEED);
      teeth.position.z = THREE.MathUtils.lerp(teeth.position.z, targetZ, SMOOTHING_SPEED);
      teeth.rotation.x = THREE.MathUtils.lerp(teeth.rotation.x, targetRotX, SMOOTHING_SPEED);
    }
  });

  return <primitive ref={group} object={scene} />;
}