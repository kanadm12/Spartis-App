"use client"

import { useState, useEffect, Suspense, useRef } from "react"
import { Header } from "./header"
import { PatientSidebar } from "./patient-sidebar"
import { Download, Share2 } from "lucide-react"
import { Canvas, useLoader } from "@react-three/fiber"
import { OrbitControls, useProgress, Html } from "@react-three/drei"
import { STLLoader } from "three-stdlib"
import * as THREE from "three"
import { useNavigate, useLocation } from "react-router-dom";

function Loader() {
  const { progress } = useProgress()
  return (
    <Html center>
      <div className="text-center">
        <p className="text-slate-400">Loading model... {Math.round(progress)}%</p>
      </div>
    </Html>
  )
}

function STLViewer({ url }: { url: string }) {
  const geometry = useLoader(STLLoader, url)

  useEffect(() => {
    geometry.computeVertexNormals()
    geometry.center()
  }, [geometry])

  return (
    // The scale was likely too small, making the model invisible.
    // STL files often use millimeters as units, so a larger scale
    // is needed to make it visible from the default camera position.
    // Starting with a scale of 1 is a safe bet.
    <mesh geometry={geometry} scale={1} castShadow receiveShadow>
      <meshStandardMaterial
        color={0xffffff}
        metalness={0.4}
        roughness={0.2}
      />
    </mesh>
  )
}

function ThreeJSSTLViewer({ url }: { url: string }) {
  return (
    <Canvas
      shadows
      dpr={[1, 2]}
      camera={{ position: [0, 0, 100], fov: 35 }}
      style={{ background: "#1a1a1a", width: "100%", height: "100%" }}
      gl={{ antialias: true, toneMapping: THREE.ACESFilmicToneMapping }}
    >
      <ambientLight intensity={0.5} />
      <directionalLight position={[50, 50, 50]} intensity={1} castShadow shadow-mapSize-width={2048} shadow-mapSize-height={2048} />
      <directionalLight position={[-50, -50, -50]} intensity={0.6} />
      <directionalLight position={[0, 50, -100]} intensity={0.4} color={new THREE.Color(0xaaaaaa)} />

      <Suspense fallback={<Loader />}>
        <STLViewer url={url} />
      </Suspense>

      <OrbitControls enableZoom enablePan enableRotate zoomSpeed={1} rotateSpeed={0.9} panSpeed={0.5} />
    </Canvas>
  )
}

export default function ViewerPage() {
  const [brightness, setBrightness] = useState(100)
  const [contrast, setContrast] = useState(100)
  const [isCopied, setIsCopied] = useState(false);

  const navigate = useNavigate()
  const location = useLocation()
  const searchParams = new URLSearchParams(location.search)
  const modelUrl = searchParams.get('url')

  const patientInfo = {
    name: "John Smith",
    id: "PT-2024-001",
    dob: "March 15, 1985",
    phone: "+1 (555) 123-4567",
    email: "john.smith@email.com",
    address: "123 Main St, City, State",
  }

  const handleBrightnessChange = (e: React.ChangeEvent<HTMLInputElement>) =>
    setBrightness(Number(e.target.value))
  const handleContrastChange = (e: React.ChangeEvent<HTMLInputElement>) =>
    setContrast(Number(e.target.value))

  const handleShare = async () => {
    if (!modelUrl) return;

    const shareData = {
      title: 'Spartis 3D Medical Scan', // You might want to pass the original filename for a better title
      text: `Check out this 3D model!`,
      url: window.location.href,
    };

    if (navigator.share) {
      try {
        await navigator.share(shareData);
        console.log('Model shared successfully');
      } catch (err) {
        console.error('Share failed:', err);
      }
    } else {
      // Fallback for browsers that don't support the Web Share API
      await navigator.clipboard.writeText(window.location.href);
      setIsCopied(true);
      // Reset the "Copied!" text after 2 seconds
      setTimeout(() => setIsCopied(false), 2000);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900">
      <Header />
      <div className="flex">
        <PatientSidebar patientInfo={patientInfo} />

        <div className="flex-1 p-6">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h1 className="text-2xl font-bold text-white">CT Scan Viewer</h1>
              <p className="text-slate-400">Viewing: Chest CT Series - June 12, 2025</p>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => navigate("/")}
                className="px-4 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-500 transition-colors flex items-center space-x-2"
              >
                <span>← Back</span>
              </button>
              <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2">
                <Download className="w-4 h-4" />
                <span>Export</span>
              </button>
              <button
                onClick={handleShare}
                className="px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600 transition-colors flex items-center space-x-2"
              >
                <Share2 className="w-4 h-4" />
                <span>{isCopied ? 'Copied!' : 'Share'}</span>
              </button>
            </div>
          </div>

          {/* CT Viewer */}
          <div className="bg-black rounded-xl overflow-hidden shadow-xl border border-slate-700 h-[calc(100vh-220px)]">
            <div className="relative h-full" style={{ filter: `brightness(${brightness}%) contrast(${contrast}%)` }}>
              {modelUrl ? <ThreeJSSTLViewer url={modelUrl} /> : <div className="text-white p-4">No model URL specified.</div>}
            </div>
          </div>

          {/* Controls */}
          <div className="flex items-center space-x-4 mt-6 p-4 bg-slate-800 rounded-lg">
            <label htmlFor="brightness-slider" className="ml-6 text-white">Brightness:</label>
            <input
              type="range"
              id="brightness-slider"
              name="brightness"
              min="50"
              max="150"
              value={brightness}
              onChange={handleBrightnessChange}
              className="w-32"
            />

            <label htmlFor="contrast-slider" className="ml-6 text-white">Contrast:</label>
            <input
              type="range"
              id="contrast-slider"
              name="contrast"
              min="50"
              max="150"
              value={contrast}
              onChange={handleContrastChange}
              className="w-32"
            />
          </div>
        </div>
      </div>
    </div>
  )
}