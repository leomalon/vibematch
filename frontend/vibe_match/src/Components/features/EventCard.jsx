import './EventCard.css';
import { getCategoryImage } from './categoryImages';

function formatPrice(precio, moneda) {
  if (precio === null || precio === undefined) return '';
  if (precio === 0) return 'Gratis';
  const prefix = moneda === 'PEN' ? 'S/' : (moneda || '') + ' ';
  return `${prefix}${precio}`;
}

export default function EventCard({ event }) {
  const price = formatPrice(event.precio, event.moneda);
  const timeStr = event.hora_inicio ? event.hora_inicio.slice(0, 5) : '';
  const dateStr = event.fecha_inicio || '';
  const imageSrc = getCategoryImage(event.categoria);
  const altText = event.categoria || 'Evento';

  return (
    <a
      className="event-card"
      href={event.url}
      target="_blank"
      rel="noopener noreferrer"
    >
      <div className="event-card__image">
        <img
          src={imageSrc}
          alt={altText}
          className="event-card__category-image"
          loading="lazy"
        />
        <div className="event-card__image-overlay" />
        <span className="event-card__badge">{event.categoria}</span>
      </div>

      <div className="event-card__body">
        <h3 className="event-card__title">{event.titulo}</h3>
        <div className="event-card__meta">
          <span>{dateStr}{dateStr && timeStr ? ' · ' : ''}{timeStr}</span>
          {price && <span className="event-card__price">{price}</span>}
        </div>
      </div>
    </a>
  );
}
