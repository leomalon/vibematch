"use client";
import { useState, useRef, useEffect } from 'react';
import { Smile, ChevronDown, Check } from 'lucide-react';
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
  const selectedArray = Array.isArray(selected) ? selected : (selected ? [selected] : []);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    function handleClick(e) {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const getLabel = () => {
    if (!selectedArray.length) return 'Moods';
    if (selectedArray.length === 1) {
      return MOODS.find(m => toSlug(m) === selectedArray[0]) || selectedArray[0];
    }
    return `${selectedArray.length} Moods`;
  };

  const handleToggle = (slug) => {
    const newSelected = selectedArray.includes(slug)
      ? selectedArray.filter(s => s !== slug)
      : [...selectedArray, slug];
    onSelect(newSelected.length === 0 ? null : newSelected);
  };

  return (
    <div className="cat-dropdown" ref={ref}>
      <button className="cat-dropdown__btn" onClick={() => setOpen(!open)}>
        <Smile size={16} />
        {getLabel()}
        <ChevronDown size={14} style={{ transform: open ? 'rotate(180deg)' : '', transition: 'transform 0.2s' }} />
      </button>

      {open && (
        <div className="cat-dropdown__menu mood-multi-select">
          <button
            className={`cat-dropdown__item ${!selectedArray.length ? 'cat-dropdown__item--active' : ''}`}
            onClick={() => { onSelect(null); setOpen(false); }}
          >
            <span>Todos</span>
            {!selectedArray.length && <Check size={14} className="cat-dropdown__check" />}
          </button>
          {MOODS.map(mood => {
            const slug = toSlug(mood);
            const isActive = selectedArray.includes(slug);
            return (
              <button
                key={mood}
                className={`cat-dropdown__item ${isActive ? 'cat-dropdown__item--active' : ''}`}
                onClick={() => handleToggle(slug)}
              >
                <span>{mood}</span>
                {isActive && <Check size={14} className="cat-dropdown__check" />}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
