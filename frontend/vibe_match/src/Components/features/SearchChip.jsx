import { Sparkles, X, ArrowLeft } from 'lucide-react';
import './SearchChip.css';

export default function SearchChip({ query, onClear }) {
  return (
    <div className="search-chip-row">
      <div className="search-chip" onClick={onClear}>
        <Sparkles size={14} className="search-chip__icon" />
        <span className="search-chip__text">{query}</span>
        <button className="search-chip__close" onClick={onClear}>
          <X size={14} />
        </button>
      </div>

      <button className="search-chip-back" onClick={onClear}>
        <ArrowLeft size={16} />
        Volver a categorías
      </button>
    </div>
  );
}
