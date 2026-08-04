'use client';
import { useState, useRef } from 'react';
import './DateFilter.css';

const PRESETS = [
  { key: 'hoy', label: 'Hoy' },
  { key: 'manana', label: 'Mañana' },
];

export default function DateFilter({ value, onChange }) {
  const [showPicker, setShowPicker] = useState(false);
  const inputRef = useRef(null);

  const isCustom = value && !PRESETS.find(p => p.key === value);

  return (
    <div className="date-filter">
      <span className="filter-label">Fecha</span>

      {PRESETS.map(p => (
        <button
          key={p.key}
          className={`pill ${value === p.key ? 'pill--active' : ''}`}
          onClick={() => onChange(p.key)}
        >
          {p.label}
        </button>
      ))}

      <div className="pill pill--icon" onClick={() => inputRef.current?.showPicker?.()}>
        📅 Elegir fecha
        <input
          ref={inputRef}
          type="date"
          className="date-filter__hidden-input"
          value={isCustom ? value : ''}
          onChange={(e) => {
            onChange(e.target.value);
            setShowPicker(false);
          }}
        />
      </div>
    </div>
  );
}
