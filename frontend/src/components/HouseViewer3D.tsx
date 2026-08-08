import React, { useState, useRef } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Html, Grid, Text } from '@react-three/drei';
import * as THREE from 'three';
import { CandidateDesign, RoomSpec } from '../types';
import {
  Eye,
  Sun,
  Moon,
  Ruler,
  Armchair,
  Layers,
  Maximize2,
  Box,
  Compass,
  CheckCircle2,
} from 'lucide-react';

interface HouseViewer3DProps {
  design: CandidateDesign;
  onSelectRoom?: (room: RoomSpec | null) => void;
}

// 3D Furniture Items Placement Engine
const FurnitureItem: React.FC<{ type: string; roomW: number; roomH: number }> = ({ type, roomW, roomH }) => {
  const isBedroom = type.includes('bedroom');
  const isLiving = type.includes('living');
  const isKitchen = type.includes('kitchen');
  const isBathroom = type.includes('bathroom');

  return (
    <group position={[0, 0.2, 0]}>
      {isBedroom && (
        <group position={[0, 0, -roomH / 4]}>
          {/* Bed frame */}
          <mesh position={[0, 0.4, 0]}>
            <boxGeometry args={[6.0, 0.8, 6.5]} />
            <meshStandardMaterial color="#475569" roughness={0.4} />
          </mesh>
          {/* Mattress */}
          <mesh position={[0, 0.9, 0.2]}>
            <boxGeometry args={[5.6, 0.6, 6.0]} />
            <meshStandardMaterial color="#F8FAFC" roughness={0.2} />
          </mesh>
          {/* Pillows */}
          <mesh position={[-1.6, 1.3, -2.0]}>
            <boxGeometry args={[1.8, 0.3, 1.2]} />
            <meshStandardMaterial color="#E2E8F0" />
          </mesh>
          <mesh position={[1.6, 1.3, -2.0]}>
            <boxGeometry args={[1.8, 0.3, 1.2]} />
            <meshStandardMaterial color="#E2E8F0" />
          </mesh>
        </group>
      )}

      {isLiving && (
        <group position={[0, 0, 0]}>
          {/* Sofa */}
          <mesh position={[0, 0.6, 2.5]}>
            <boxGeometry args={[8.0, 1.2, 2.8]} />
            <meshStandardMaterial color="#312E81" roughness={0.3} />
          </mesh>
          {/* Coffee Table */}
          <mesh position={[0, 0.4, -0.5]}>
            <boxGeometry args={[4.5, 0.6, 2.2]} />
            <meshStandardMaterial color="#78350F" roughness={0.6} />
          </mesh>
          {/* TV Unit */}
          <mesh position={[0, 0.8, -roomH / 2.5]}>
            <boxGeometry args={[6.5, 1.4, 1.0]} />
            <meshStandardMaterial color="#1E293B" />
          </mesh>
        </group>
      )}

      {isKitchen && (
        <group position={[-roomW / 3, 0, 0]}>
          {/* Counter top */}
          <mesh position={[0, 1.2, 0]}>
            <boxGeometry args={[3.0, 2.4, roomH * 0.7]} />
            <meshStandardMaterial color="#334155" roughness={0.1} />
          </mesh>
          {/* Refrigerator */}
          <mesh position={[0, 2.5, roomH / 3]}>
            <boxGeometry args={[2.8, 5.0, 2.8]} />
            <meshStandardMaterial color="#94A3B8" metalness={0.8} roughness={0.2} />
          </mesh>
        </group>
      )}

      {isBathroom && (
        <group position={[0, 0, 0]}>
          {/* Toilet */}
          <mesh position={[-roomW / 3, 0.8, 0]}>
            <boxGeometry args={[1.5, 1.6, 2.2]} />
            <meshStandardMaterial color="#FFFFFF" roughness={0.1} />
          </mesh>
          {/* Wash basin */}
          <mesh position={[roomW / 3, 1.2, 0]}>
            <boxGeometry args={[1.8, 2.2, 1.5]} />
            <meshStandardMaterial color="#F1F5F9" roughness={0.1} />
          </mesh>
        </group>
      )}
    </group>
  );
};

// 3D Room Box Mesh with Walls, Floor, Ceiling & Doorways
const Room3DMesh: React.FC<{
  room: RoomSpec;
  isSelected: boolean;
  activeFloor: number;
  showFurniture: boolean;
  showMeasurements: boolean;
  transparentWalls: boolean;
  onClick: () => void;
}> = ({
  room,
  isSelected,
  activeFloor,
  showFurniture,
  showMeasurements,
  transparentWalls,
  onClick,
}) => {
  const isFloorVisible = activeFloor === 0 || activeFloor === room.floor;
  if (!isFloorVisible) return null;

  const wallHeight = 8.0;
  const floorOffsetY = (room.floor - 1) * (wallHeight + 0.5);

  const posX = room.x + room.width / 2;
  const posZ = room.y + room.height / 2;

  const roomColors: Record<string, string> = {
    living_room: '#6366F1',
    master_bedroom: '#8B5CF6',
    bedroom_2: '#EC4899',
    bedroom_3: '#F43F5E',
    kitchen: '#10B981',
    dining_room: '#F59E0B',
    bathroom_1: '#06B6D4',
    bathroom_2: '#0EA5E9',
    garage_parking: '#64748B',
    staircase: '#D97706',
  };

  const baseColor = roomColors[room.type] || '#475569';

  return (
    <group position={[posX, floorOffsetY, posZ]} onClick={(e) => { e.stopPropagation(); onClick(); }}>
      {/* Room Floor Slab */}
      <mesh position={[0, 0.1, 0]}>
        <boxGeometry args={[room.width - 0.2, 0.2, room.height - 0.2]} />
        <meshStandardMaterial
          color={isSelected ? '#6366F1' : baseColor}
          roughness={0.5}
          metalness={0.1}
        />
      </mesh>

      {/* Exterior Walls */}
      <mesh position={[0, wallHeight / 2, 0]}>
        <boxGeometry args={[room.width, wallHeight, room.height]} />
        <meshStandardMaterial
          color={isSelected ? '#818CF8' : '#334155'}
          wireframe={transparentWalls}
          transparent={true}
          opacity={transparentWalls ? 0.3 : isSelected ? 0.6 : 0.85}
          roughness={0.7}
        />
      </mesh>

      {/* 3D Furniture Population */}
      {showFurniture && (
        <FurnitureItem type={room.type} roomW={room.width} roomH={room.height} />
      )}

      {/* Room Label in 3D */}
      <Html position={[0, wallHeight + 1.2, 0]} center distanceFactor={40}>
        <div
          className={`px-2.5 py-1 rounded-md text-xs font-semibold whitespace-nowrap shadow-lg transition-all cursor-pointer ${
            isSelected
              ? 'bg-indigo-600 text-white ring-2 ring-indigo-400 glow-indigo'
              : 'bg-dark-800/90 text-slate-200 border border-slate-700/80 hover:bg-slate-800'
          }`}
        >
          {room.name}
          <div className="text-[10px] text-slate-400 font-normal">
            {room.width} x {room.height} ft ({Math.round(room.width * room.height)} sq ft)
          </div>
        </div>
      </Html>

      {/* Measurement Annotations */}
      {showMeasurements && (
        <group position={[0, 0.3, 0]}>
          <Html position={[0, 0, room.height / 2 + 0.5]} center distanceFactor={35}>
            <span className="bg-emerald-950/80 text-emerald-400 border border-emerald-500/30 px-1.5 py-0.5 rounded text-[10px] font-mono">
              {room.width} ft
            </span>
          </Html>
          <Html position={[room.width / 2 + 0.5, 0, 0]} center distanceFactor={35}>
            <span className="bg-emerald-950/80 text-emerald-400 border border-emerald-500/30 px-1.5 py-0.5 rounded text-[10px] font-mono">
              {room.height} ft
            </span>
          </Html>
        </group>
      )}
    </group>
  );
};

export const HouseViewer3D: React.FC<HouseViewer3DProps> = ({ design, onSelectRoom }) => {
  const [activeFloor, setActiveFloor] = useState<number>(0); // 0 = all floors
  const [viewMode, setViewMode] = useState<'exterior' | 'interior' | 'top'>('exterior');
  const [isNightMode, setIsNightMode] = useState<boolean>(false);
  const [showFurniture, setShowFurniture] = useState<boolean>(true);
  const [showMeasurements, setShowMeasurements] = useState<boolean>(true);
  const [transparentWalls, setTransparentWalls] = useState<boolean>(false);
  const [selectedRoom, setSelectedRoom] = useState<RoomSpec | null>(null);

  const handleRoomClick = (room: RoomSpec) => {
    setSelectedRoom(room);
    if (onSelectRoom) onSelectRoom(room);
  };

  const plotW = design.rooms.reduce((max, r) => Math.max(max, r.x + r.width), 40) + 10;
  const plotL = design.rooms.reduce((max, r) => Math.max(max, r.y + r.height), 40) + 10;

  // Camera presets
  const cameraPresets = {
    exterior: [plotW * 0.9, plotW * 0.8, plotL * 1.1] as [number, number, number],
    interior: [plotW / 2, 8, plotL / 2 + 10] as [number, number, number],
    top: [plotW / 2, plotW * 1.4, plotL / 2 + 0.1] as [number, number, number],
  };

  return (
    <div className="relative w-full h-[650px] bg-dark-900 rounded-2xl overflow-hidden border border-slate-800 shadow-2xl flex flex-col">
      {/* Top Controls Toolbar */}
      <div className="absolute top-4 left-4 right-4 z-20 flex flex-wrap items-center justify-between gap-3 pointer-events-auto bg-dark-800/85 backdrop-blur-md p-2.5 rounded-xl border border-slate-700/60 shadow-xl">
        {/* Floor Selector */}
        <div className="flex items-center gap-1 bg-dark-900/80 p-1 rounded-lg border border-slate-700/50">
          <span className="text-xs font-semibold text-slate-400 px-2 flex items-center gap-1">
            <Layers className="w-3.5 h-3.5 text-indigo-400" /> Floor:
          </span>
          {[0, 1, 2, 3].map((fl) => (
            <button
              key={fl}
              onClick={() => setActiveFloor(fl)}
              className={`px-2.5 py-1 text-xs rounded-md font-medium transition-all ${
                activeFloor === fl
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              {fl === 0 ? 'All' : `L${fl}`}
            </button>
          ))}
        </div>

        {/* Camera Perspective Modes */}
        <div className="flex items-center gap-1 bg-dark-900/80 p-1 rounded-lg border border-slate-700/50">
          <button
            onClick={() => setViewMode('exterior')}
            className={`px-2.5 py-1 text-xs rounded-md font-medium flex items-center gap-1 transition-all ${
              viewMode === 'exterior'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            <Maximize2 className="w-3.5 h-3.5" /> Exterior
          </button>
          <button
            onClick={() => setViewMode('interior')}
            className={`px-2.5 py-1 text-xs rounded-md font-medium flex items-center gap-1 transition-all ${
              viewMode === 'interior'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            <Eye className="w-3.5 h-3.5" /> Walkthrough
          </button>
          <button
            onClick={() => setViewMode('top')}
            className={`px-2.5 py-1 text-xs rounded-md font-medium flex items-center gap-1 transition-all ${
              viewMode === 'top'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            <Compass className="w-3.5 h-3.5" /> Top View
          </button>
        </div>

        {/* Feature Toggles */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsNightMode(!isNightMode)}
            className={`p-1.5 rounded-lg border transition-all ${
              isNightMode
                ? 'bg-indigo-950 text-amber-300 border-indigo-500/50'
                : 'bg-slate-800 text-slate-300 border-slate-700 hover:text-white'
            }`}
            title="Day / Night lighting toggle"
          >
            {isNightMode ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
          </button>

          <button
            onClick={() => setShowFurniture(!showFurniture)}
            className={`p-1.5 rounded-lg border transition-all ${
              showFurniture
                ? 'bg-indigo-600 text-white border-indigo-400'
                : 'bg-slate-800 text-slate-400 border-slate-700'
            }`}
            title="Toggle furniture 3D models"
          >
            <Armchair className="w-4 h-4" />
          </button>

          <button
            onClick={() => setShowMeasurements(!showMeasurements)}
            className={`p-1.5 rounded-lg border transition-all ${
              showMeasurements
                ? 'bg-emerald-600 text-white border-emerald-400'
                : 'bg-slate-800 text-slate-400 border-slate-700'
            }`}
            title="Toggle measurement tags"
          >
            <Ruler className="w-4 h-4" />
          </button>

          <button
            onClick={() => setTransparentWalls(!transparentWalls)}
            className={`p-1.5 rounded-lg border transition-all ${
              transparentWalls
                ? 'bg-cyan-600 text-white border-cyan-400'
                : 'bg-slate-800 text-slate-400 border-slate-700'
            }`}
            title="Toggle see-through wall structure"
          >
            <Box className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* 3D Canvas Renders */}
      <div className="w-full h-full">
        <Canvas
          camera={{ position: cameraPresets[viewMode], fov: 45 }}
          shadows
          onPointerMissed={() => setSelectedRoom(null)}
        >
          {/* Lighting */}
          <ambientLight intensity={isNightMode ? 0.2 : 0.75} />
          <directionalLight
            position={[40, 60, 40]}
            intensity={isNightMode ? 0.3 : 1.2}
            castShadow
            shadow-mapSize-width={2048}
            shadow-mapSize-height={2048}
          />
          {isNightMode && (
            <pointLight position={[plotW / 2, 20, plotL / 2]} intensity={2.5} color="#F59E0B" />
          )}

          {/* Plot Grid Floor */}
          <Grid
            position={[plotW / 2, -0.1, plotL / 2]}
            args={[plotW * 1.8, plotL * 1.8]}
            cellSize={5}
            cellThickness={1}
            cellColor="#334155"
            sectionSize={20}
            sectionThickness={1.5}
            sectionColor="#6366F1"
            fadeDistance={200}
          />

          {/* Render 3D Rooms */}
          {design.rooms.map((room) => (
            <Room3DMesh
              key={room.id}
              room={room}
              isSelected={selectedRoom?.id === room.id}
              activeFloor={activeFloor}
              showFurniture={showFurniture}
              showMeasurements={showMeasurements}
              transparentWalls={transparentWalls}
              onClick={() => handleRoomClick(room)}
            />
          ))}

          <OrbitControls makeDefault maxPolarAngle={Math.PI / 2.05} />
        </Canvas>
      </div>

      {/* Selected Room Floating Properties Overlay */}
      {selectedRoom && (
        <div className="absolute bottom-4 right-4 z-20 bg-dark-800/90 backdrop-blur-md p-4 rounded-xl border border-indigo-500/40 shadow-2xl w-72 text-xs">
          <div className="flex items-center justify-between mb-2">
            <span className="font-bold text-sm text-indigo-400 flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-indigo-400" /> {selectedRoom.name}
            </span>
            <span className="text-[10px] bg-indigo-950 text-indigo-300 border border-indigo-500/30 px-2 py-0.5 rounded font-mono">
              Floor {selectedRoom.floor}
            </span>
          </div>
          <div className="space-y-1.5 text-slate-300">
            <div className="flex justify-between">
              <span className="text-slate-400">Dimensions:</span>
              <span className="font-mono font-medium text-white">{selectedRoom.width} ft x {selectedRoom.height} ft</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Total Area:</span>
              <span className="font-mono font-medium text-emerald-400">{Math.round(selectedRoom.width * selectedRoom.height)} sq ft</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Coordinates:</span>
              <span className="font-mono text-slate-400">X: {selectedRoom.x}, Y: {selectedRoom.y}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
