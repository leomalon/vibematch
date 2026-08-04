'use client';
import { useState, useRef, useEffect } from 'react';
import { Smile, ChevronDown } from 'lucide-react';
import './CategoryDropdown.css';

const MOODS = [
  'Romántico', 'Energético', 'Relajado', 'Misterioso', 'Divertido',
  'Cultural', 'Artístico', 'Nocturno', 'Familiar', 'Intenso',
  'Fiesta', 'Educativo', 'Espontáneo', 'Elegante', 'Underground',
  'Deportivo', 'Gastronómico', 'Urbano', 'Desconexión', 'Aire-libre',
  'Natural', 'Aventurero', 'Foodie', 'Casual', 'Buen-ambiente',
  'Extremo', 'Íntimo', 'Aesthetic',
];

function toSlug(text) {
  return text
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/\s+/g, '-');
}

export default function MoodFilter({ selected, onSelect }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    function handleClick(e) {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const label = selected
    ? MOODS.find(m => toSlug(m) === selected) || selected
    : 'Moods';

  return (
    <div className="cat-dropdown" ref={ref}>
      <button className="cat-dropdown__btn" onClick={() => setOpen(!open)}>
        <Smile size={16} />
        {label}
        <ChevronDown size={14} style={{ transform: open ? 'rotate(180deg)' : '', transition: 'transform 0.2s' }} />
      </button>

      {open && (
        <div className="cat-dropdown__menu">
          <button
            className={`cat-dropdown__item ${!selected ? 'cat-dropdown__item--active' : ''}`}
            onClick={() => { onSelect(null); setOpen(false); }}
          >
            Todos
          </button>
          {MOODS.map(mood => (
            <button
              key={mood}
              className={`cat-dropdown__item ${toSlug(mood) === selected ? 'cat-dropdown__item--active' : ''}`}
              onClick={() => { onSelect(toSlug(mood)); setOpen(false); }}
            >
              {mood}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
