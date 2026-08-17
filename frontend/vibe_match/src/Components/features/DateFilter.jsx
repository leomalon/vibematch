'use client';
import { useState, useRef, useEffect } from 'react';
import { Calendar } from 'lucide-react';
import dynamic from 'next/dynamic';
import './DateFilter.css';

const CalendarPicker = dynamic(() => import('./CalendarPicker'), { ssr: false });

const PRESETS = [
  { key: 'hoy', label: 'Hoy' },
  { key: 'manana', label: 'Mañana' },
];

export default function DateFilter({ value, onChange }) {
  const [showCalendar, setShowCalendar] = useState(false);
  const pickerRef = useRef(null);
  const triggerRef = useRef(null);

  const isCustom = value && !PRESETS.find(p => p.key === value);

  const handleDateSelect = (dateStr) => {
    if (dateStr === null) {
      onChange('hoy'); // Default to "hoy" when cleared
    } else {
      onChange(dateStr);
    }
    setShowCalendar(false);
  };

  const handleCalendarClose = () => {
    setShowCalendar(false);
  };

  const toggleCalendar = (e) => {
    e.stopPropagation();
    setShowCalendar(!showCalendar);
  };

  return (
    <div className="date-filter">
      <span className="filter-label">Fecha</span>

      {PRESETS.map(p => (
        <button
          key={p.key}
          className={`pill ${value === p.key ? 'pill--active' : ''}`}
          onClick={() => {
            setShowCalendar(false);
            onChange(p.key);
          }}
        >
          {p.label}
        </button>
      ))}

      <div className="date-filter__custom-wrap">
        <button
          ref={triggerRef}
          className={`pill pill--icon ${isCustom || showCalendar ? 'pill--active' : ''}`}
          onClick={toggleCalendar}
        >
          <Calendar size={14} />
          Elegir fecha
        </button>

        {showCalendar && (
          <CalendarPicker
            ref={pickerRef}
            selectedDate={isCustom ? value : null}
            onSelect={handleDateSelect}
            onClose={handleCalendarClose}
            isOpen={showCalendar}
          />
        )}
      </div>
    </div>
  );
}
