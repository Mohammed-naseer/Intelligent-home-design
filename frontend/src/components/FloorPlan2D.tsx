import React, { useRef, useEffect } from 'react';
import { CandidateDesign, RoomSpec } from '../types';

interface FloorPlan2DProps {
  design: CandidateDesign;
  activeFloor?: number;
  width?: number;
  height?: number;
}

const ROOM_COLOR_MAP: Record<string, string> = {
  living_room:      '#6366F1',
  master_bedroom:   '#8B5CF6',
  bedroom_2:        '#EC4899',
  bedroom_3:        '#F43F5E',
  bedroom_4:        '#FB7185',
  kitchen:          '#10B981',
  dining_room:      '#F59E0B',
  bathroom_1:       '#06B6D4',
  bathroom_2:       '#0EA5E9',
  bathroom_3:       '#38BDF8',
  foyer:            '#A78BFA',
  corridor:         '#94A3B8',
  staircase:        '#D97706',
  balcony:          '#34D399',
  garage_parking:   '#64748B',
  home_office:      '#60A5FA',
};

export const FloorPlan2D: React.FC<FloorPlan2DProps> = ({
  design,
  activeFloor = 0,
  width = 500,
  height = 400,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, width, height);

    // Background
    ctx.fillStyle = '#0B0F19';
    ctx.fillRect(0, 0, width, height);

    const visibleRooms = activeFloor === 0
      ? design.rooms
      : design.rooms.filter(r => r.floor === activeFloor);

    if (visibleRooms.length === 0) return;

    // Compute bounding box
    const maxX = Math.max(...visibleRooms.map(r => r.x + r.width));
    const maxY = Math.max(...visibleRooms.map(r => r.y + r.height));
    const padding = 30;

    const scaleX = (width - padding * 2) / maxX;
    const scaleY = (height - padding * 2) / maxY;
    const scale = Math.min(scaleX, scaleY);

    // Draw grid
    ctx.strokeStyle = 'rgba(255,255,255,0.04)';
    ctx.lineWidth = 0.5;
    const gridStep = 10 * scale;
    for (let gx = padding; gx < width - padding; gx += gridStep) {
      ctx.beginPath(); ctx.moveTo(gx, padding); ctx.lineTo(gx, height - padding); ctx.stroke();
    }
    for (let gy = padding; gy < height - padding; gy += gridStep) {
      ctx.beginPath(); ctx.moveTo(padding, gy); ctx.lineTo(width - padding, gy); ctx.stroke();
    }

    // Draw plot boundary
    ctx.strokeStyle = 'rgba(99,102,241,0.4)';
    ctx.lineWidth = 1.5;
    ctx.strokeRect(padding, padding, maxX * scale, maxY * scale);

    // Draw each room
    visibleRooms.forEach(room => {
      const rx = padding + room.x * scale;
      const ry = padding + room.y * scale;
      const rw = room.width * scale;
      const rh = room.height * scale;

      const baseColor = ROOM_COLOR_MAP[room.type] || '#475569';

      // Fill
      ctx.fillStyle = `${baseColor}33`;
      ctx.fillRect(rx, ry, rw, rh);

      // Border
      ctx.strokeStyle = baseColor;
      ctx.lineWidth = 1.5;
      ctx.strokeRect(rx, ry, rw, rh);

      // Room label
      ctx.fillStyle = '#F8FAFC';
      ctx.font = `bold ${Math.max(9, Math.min(12, rw / 7))}px Inter, sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';

      const labelX = rx + rw / 2;
      const labelY = ry + rh / 2 - 8;
      ctx.fillText(room.name, labelX, labelY, rw - 4);

      // Dimensions label
      ctx.font = `${Math.max(7, Math.min(10, rw / 9))}px monospace`;
      ctx.fillStyle = baseColor;
      ctx.fillText(`${room.width}×${room.height} ft`, labelX, labelY + 14, rw - 4);
    });

    // Floor label
    ctx.fillStyle = 'rgba(99,102,241,0.9)';
    ctx.font = 'bold 11px Inter, sans-serif';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    ctx.fillText(activeFloor === 0 ? 'All Floors' : `Floor ${activeFloor}`, padding + 6, padding + 6);

  }, [design, activeFloor, width, height]);

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      className="rounded-xl border border-slate-800 w-full"
      style={{ maxWidth: width }}
    />
  );
};
