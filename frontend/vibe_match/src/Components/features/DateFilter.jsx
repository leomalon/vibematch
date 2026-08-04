'use client';
import { useRef } from 'react';
import { Calendar } from 'lucide-react';
import './DateFilter.css';

const PRESETS = [
  { key: 'hoy', label: 'Hoy' },
  { key: 'manana', label: 'Mañana' },
];

export default function DateFilter({ value, onChange }) {
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

      <div className={`pill pill--icon ${isCustom ? 'pill--active' : ''}`} onClick={() => inputRef.current?.showPicker?.()}>
        <Calendar size={14} />
        Elegir fecha
        <input
          ref={inputRef}
          type="date"
          className="date-filter__hidden-input"
          value={isCustom ? value : ''}
          onChange={(e) => onChange(e.target.value)}
        />
      </div>
    </div>
  );
}
