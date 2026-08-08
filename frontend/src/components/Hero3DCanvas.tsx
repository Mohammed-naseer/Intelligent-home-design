import React, { useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Float, MeshWobbleMaterial, Text, PerspectiveCamera } from '@react-three/drei';
import * as THREE from 'three';
import { Eye, Sun, Moon, Layers, Box, Sparkles } from 'lucide-react';

// ── 3D House Structure Component ──────────────────────────────────────────────
const House3DModel = ({ mode }: { mode: 'solid' | 'wireframe' | 'xray' }) => {
  const groupRef = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = state.clock.getElapsedTime() * 0.15;
    }
  });

  const isWireframe = mode === 'wireframe';
  const opacity = mode === 'xray' ? 0.45 : 0.9;

  return (
    <group ref={groupRef} position={[0, -0.5, 0]}>
      {/* Ground Slab / Foundation */}
      <mesh position={[0, 0, 0]} receiveShadow>
        <boxGeometry args={[7, 0.3, 6]} />
        <meshStandardMaterial
          color="#1e293b"
          roughness={0.4}
          metalness={0.8}
          wireframe={isWireframe}
        />
      </mesh>

      {/* Ground Floor Living & Dining */}
      <mesh position={[-1.2, 0.95, -0.5]} castShadow receiveShadow>
        <boxGeometry args={[4, 1.6, 4]} />
        <meshPhysicalMaterial
          color="#312e81"
          roughness={0.2}
          metalness={0.5}
          transmission={mode === 'xray' ? 0.6 : 0.1}
          opacity={opacity}
          transparent
          wireframe={isWireframe}
        />
      </mesh>

      {/* Ground Floor Kitchen & Utility */}
      <mesh position={[2, 0.95, 0.5]} castShadow receiveShadow>
        <boxGeometry args={[2.2, 1.6, 2.5]} />
        <meshPhysicalMaterial
          color="#065f46"
          roughness={0.3}
          metalness={0.6}
          opacity={opacity}
          transparent
          wireframe={isWireframe}
        />
      </mesh>

      {/* First Floor Bedrooms */}
      <mesh position={[-0.8, 2.45, 0.2]} castShadow receiveShadow>
        <boxGeometry args={[4.2, 1.4, 3.8]} />
        <meshPhysicalMaterial
          color="#4c1d95"
          roughness={0.25}
          metalness={0.4}
          opacity={opacity}
          transparent
          wireframe={isWireframe}
        />
      </mesh>

      {/* First Floor Balcony & Glass Railing */}
      <mesh position={[1.8, 2.15, -1.2]}>
        <boxGeometry args={[2.2, 0.8, 1.2]} />
        <meshPhysicalMaterial
          color="#38bdf8"
          roughness={0.1}
          transmission={0.85}
          transparent
          opacity={0.8}
          wireframe={isWireframe}
        />
      </mesh>

      {/* Modern Cantilever Roof */}
      <mesh position={[0, 3.35, 0]}>
        <boxGeometry args={[7.2, 0.25, 6.2]} />
        <meshStandardMaterial
          color="#0f172a"
          roughness={0.3}
          metalness={0.9}
          wireframe={isWireframe}
        />
      </mesh>

      {/* Floating 3D Accent Lights inside rooms */}
      <pointLight position={[-1.2, 1.2, -0.5]} color="#818cf8" intensity={2.5} distance={5} />
      <pointLight position={[2, 1.2, 0.5]} color="#34d399" intensity={2} distance={4} />
      <pointLight position={[-0.8, 2.6, 0.2]} color="#c084fc" intensity={2.5} distance={5} />

      {/* Solar Panel Accents on Roof */}
      <mesh position={[-1.5, 3.48, 0]} rotation={[-0.1, 0, 0]}>
        <boxGeometry args={[3, 0.05, 4]} />
        <meshStandardMaterial color="#0284c7" roughness={0.1} metalness={0.95} />
      </mesh>
    </group>
  );
};

// ── Floating Decorative Elements ──────────────────────────────────────────────
const FloatingOrbs = () => {
  return (
    <>
      <Float speed={2} rotationIntensity={0.5} floatIntensity={1}>
        <mesh position={[-4, 2, -2]}>
          <octahedronGeometry args={[0.5, 0]} />
          <MeshWobbleMaterial color="#6366f1" factor={0.6} speed={2} wireframe />
        </mesh>
      </Float>
      <Float speed={1.5} rotationIntensity={0.8} floatIntensity={1.2}>
        <mesh position={[4, 3, 2]}>
          <icosahedronGeometry args={[0.6, 0]} />
          <MeshWobbleMaterial color="#10b981" factor={0.4} speed={1.5} wireframe />
        </mesh>
      </Float>
      <Float speed={2.5} rotationIntensity={0.4} floatIntensity={0.8}>
        <mesh position={[3.5, -1.5, -1]}>
          <torusGeometry args={[0.4, 0.15, 16, 32]} />
          <meshStandardMaterial color="#8b5cf6" metalness={0.8} roughness={0.2} />
        </mesh>
      </Float>
    </>
  );
};

// ── Main Hero3DCanvas Component ───────────────────────────────────────────────
export const Hero3DCanvas: React.FC = () => {
  const [renderMode, setRenderMode] = useState<'solid' | 'wireframe' | 'xray'>('solid');
  const [isDay, setIsDay] = useState<boolean>(false);
  const [autoRotate, setAutoRotate] = useState<boolean>(true);

  return (
    <div className="relative w-full h-[480px] sm:h-[540px] rounded-3xl overflow-hidden glass-card border border-indigo-500/20 shadow-2xl">
      {/* Top 3D Control Bar Overlay */}
      <div className="absolute top-4 left-4 right-4 z-20 flex flex-wrap items-center justify-between gap-3 pointer-events-auto">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-dark-900/80 backdrop-blur-md border border-slate-700/60 text-xs text-indigo-300 font-mono shadow-lg">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400 animate-pulse" />
          <span>Interactive 3D Spatial Engine</span>
        </div>

        <div className="flex items-center gap-2 bg-dark-900/80 backdrop-blur-md border border-slate-700/60 p-1 rounded-xl shadow-lg">
          <button
            onClick={() => setRenderMode('solid')}
            className={`px-3 py-1 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
              renderMode === 'solid'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
            title="Solid Render Mode"
          >
            <Box className="w-3.5 h-3.5" /> Solid
          </button>
          <button
            onClick={() => setRenderMode('wireframe')}
            className={`px-3 py-1 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
              renderMode === 'wireframe'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
            title="Wireframe Mesh Mode"
          >
            <Layers className="w-3.5 h-3.5" /> Wireframe
          </button>
          <button
            onClick={() => setRenderMode('xray')}
            className={`px-3 py-1 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
              renderMode === 'xray'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
            title="X-Ray Transparent View"
          >
            <Eye className="w-3.5 h-3.5" /> X-Ray
          </button>
          <div className="h-4 w-[1px] bg-slate-700 mx-0.5" />
          <button
            onClick={() => setIsDay(!isDay)}
            className="p-1.5 rounded-lg text-slate-400 hover:text-amber-300 transition-all"
            title={isDay ? 'Switch to Night Ambient' : 'Switch to Day Light'}
          >
            {isDay ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-indigo-300" />}
          </button>
        </div>
      </div>

      {/* Canvas Scene */}
      <Canvas shadows className="w-full h-full cursor-grab active:cursor-grabbing">
        <PerspectiveCamera makeDefault position={[7, 5, 8]} fov={45} />
        <OrbitControls
          enableZoom={true}
          maxPolarAngle={Math.PI / 2.1}
          minDistance={4}
          maxDistance={14}
          autoRotate={autoRotate}
          autoRotateSpeed={0.8}
        />

        {/* Ambient & Directional Lighting */}
        <ambientLight intensity={isDay ? 1.2 : 0.4} />
        <directionalLight
          position={[10, 15, 8]}
          intensity={isDay ? 2.5 : 1.0}
          castShadow
          shadow-mapSize-width={2048}
          shadow-mapSize-height={2048}
          color={isDay ? '#fffbeb' : '#818cf8'}
        />
        <pointLight position={[-10, 10, -10]} intensity={0.5} color="#ec4899" />

        {/* Background Environment Fog */}
        <color attach="background" args={[isDay ? '#0f172a' : '#04060d']} />
        <fog attach="fog" args={[isDay ? '#0f172a' : '#04060d', 10, 22]} />

        {/* 3D House Model & Orbs */}
        <House3DModel mode={renderMode} />
        <FloatingOrbs />

        {/* Grid floor */}
        <gridHelper args={[24, 24, '#334155', '#1e293b']} position={[0, -0.51, 0]} />
      </Canvas>

      {/* Bottom Floating Hint Overlay */}
      <div className="absolute bottom-4 left-4 right-4 z-20 flex items-center justify-between pointer-events-none">
        <div className="px-3 py-1.5 rounded-xl bg-dark-900/80 backdrop-blur-md border border-slate-800 text-[11px] text-slate-400 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          <span>Click & Drag to Orbit 3D Model | Scroll to Zoom</span>
        </div>
        <button
          onClick={() => setAutoRotate(!autoRotate)}
          className="pointer-events-auto px-3 py-1.5 rounded-xl bg-dark-900/80 backdrop-blur-md border border-slate-700/60 text-[11px] font-medium text-slate-300 hover:text-white transition-all"
        >
          Auto-Rotate: <span className={autoRotate ? 'text-emerald-400' : 'text-slate-500'}>{autoRotate ? 'ON' : 'OFF'}</span>
        </button>
      </div>
    </div>
  );
};
