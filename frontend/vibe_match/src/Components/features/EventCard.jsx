import './EventCard.css';

function toSlug(text) {
  return text
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/\s+/g, '-');
}

function formatPrice(precio, moneda) {
  if (precio === null || precio === undefined) return '';
  if (precio === 0) return 'Gratis';
  const prefix = moneda === 'PEN' ? 'S/' : (moneda || '') + ' ';
  return `${prefix}${precio}`;
}

export default function EventCard({ event }) {
  const slug = toSlug(event.categoria || '');
  const price = formatPrice(event.precio, event.moneda);
  const timeStr = event.hora_inicio ? event.hora_inicio.slice(0, 5) : '';
  const dateStr = event.fecha_inicio || '';

  return (
    <a
      className="event-card"
      href={event.url}
      target="_blank"
      rel="noopener noreferrer"
    >
      <div className={`event-card__image grad-${slug}`}>
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
