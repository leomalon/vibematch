'use client';
import { useState, useRef, useEffect } from 'react';
import './PriceFilter.css';

export default function PriceFilter({ value, onChange }) {
  const [showRange, setShowRange] = useState(false);
  const [min, setMin] = useState('');
  const [max, setMax] = useState('');
  const wrapRef = useRef(null);

  const isCustom = value === 'custom';

  // Close dropdown when clicking outside
  useEffect(() => {
    if (typeof window === 'undefined') return;
    function handleClick(e) {
      if (wrapRef.current && !wrapRef.current.contains(e.target)) {
        setShowRange(false);
      }
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  function handleGratis() {
    setShowRange(false);
    onChange('gratis', 0);
  }

  function handleCustom() {
    if (min || max) {
      onChange('custom', max ? Number(max) : undefined, min ? Number(min) : undefined);
    }
  }

  function handleClearCustom() {
    setMin('');
    setMax('');
    setShowRange(false);
    onChange('gratis', 0);
  }

  return (
    <div className="price-filter" ref={wrapRef}>
      <span className="filter-label">Precio</span>

      <button
        className={`pill ${value === 'gratis' ? 'pill--active' : ''}`}
        onClick={handleGratis}
      >
        Gratis
      </button>

      <div className="price-filter__custom-wrap">
        <button
          className={`pill pill--icon ${isCustom ? 'pill--active' : ''}`}
          onClick={() => setShowRange(!showRange)}
        >
          Elegir rango
        </button>

        {showRange && (
          <div className="price-filter__range">
            <input
              type="number"
              placeholder="Mín (S/.)"
              value={min}
              onChange={e => setMin(e.target.value)}
              className="price-filter__input"
              min="0"
            />
            <span className="price-filter__sep">–</span>
            <input
              type="number"
              placeholder="Máx (S/.)"
              value={max}
              onChange={e => setMax(e.target.value)}
              className="price-filter__input"
              min="0"
            />
            <button className="price-filter__apply" onClick={handleCustom}>Aplicar</button>
            <button className="price-filter__clear" onClick={handleClearCustom}>Limpiar</button>
          </div>
        )}
      </div>
    </div>
  );
}
