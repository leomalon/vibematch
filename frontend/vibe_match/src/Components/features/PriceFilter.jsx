'use client';
import { useState } from 'react';
import './PriceFilter.css';

const PRESETS = [
  { key: 'gratis', label: 'Gratis', max: 0 },
  { key: '20', label: '< 20 S/.', max: 20 },
  { key: '50', label: '< 50 S/.', max: 50 },
];

export default function PriceFilter({ value, onChange }) {
  const [showRange, setShowRange] = useState(false);
  const [min, setMin] = useState('');
  const [max, setMax] = useState('');

  const isCustom = value && !PRESETS.find(p => p.key === value);

  function handlePreset(key, maxVal) {
    setShowRange(false);
    onChange(key, maxVal);
  }

  function handleCustom() {
    if (min || max) {
      onChange('custom', max ? Number(max) : undefined, min ? Number(min) : undefined);
    }
  }

  return (
    <div className="price-filter">
      <span className="filter-label">Precio</span>

      {PRESETS.map(p => (
        <button
          key={p.key}
          className={`pill ${value === p.key ? 'pill--active' : ''}`}
          onClick={() => handlePreset(p.key, p.max)}
        >
          {p.label}
        </button>
      ))}

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
              placeholder="Mín"
              value={min}
              onChange={e => setMin(e.target.value)}
              className="price-filter__input"
            />
            <span className="price-filter__sep">–</span>
            <input
              type="number"
              placeholder="Máx"
              value={max}
              onChange={e => setMax(e.target.value)}
              className="price-filter__input"
            />
            <button className="price-filter__apply" onClick={handleCustom}>OK</button>
          </div>
        )}
      </div>
    </div>
  );
}
