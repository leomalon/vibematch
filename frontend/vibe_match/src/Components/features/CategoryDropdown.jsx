"use client";
import { useState, useRef, useEffect } from 'react';
import { ChevronDown, LayoutGrid } from 'lucide-react';
import './CategoryDropdown.css';

const CATEGORIES = [
  'Arte-cultura', 'Teatro', 'Conciertos', 'Entretenimiento',
  'Bar', 'Restaurante', 'Huarique', 'Heladería', 'Cafetería',
  'Rooftop', 'Playa', 'Hotel', 'Deportes', 'Viaje-aventura',
  'Paseo', 'Ocio', 'Fútbol', 'Cursos-talleres',
  'Seminarios-Conferencias', 'Stand-up',
];

function toSlug(text) {
  return text
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/\s+/g, '-');
}

export default function CategoryDropdown({ selected, onSelect }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    function handleClick(e) {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const label = selected
    ? CATEGORIES.find(c => toSlug(c) === selected) || selected
    : 'Categorías';

  return (
    <div className="cat-dropdown" ref={ref}>
      <button className="cat-dropdown__btn" onClick={() => setOpen(!open)}>
        <LayoutGrid size={16} />
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
          {CATEGORIES.map(cat => (
            <button
              key={cat}
              className={`cat-dropdown__item ${toSlug(cat) === selected ? 'cat-dropdown__item--active' : ''}`}
              onClick={() => { onSelect(toSlug(cat)); setOpen(false); }}
            >
              {cat}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
