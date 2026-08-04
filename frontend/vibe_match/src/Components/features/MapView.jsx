'use client';
import { useEffect, useRef } from 'react';
import './MapView.css';

const LIMA_CENTER = [-12.05, -77.04];

function formatPrice(precio, moneda) {
  if (precio === null || precio === undefined) return '';
  if (precio === 0) return 'Gratis';
  return `${moneda === 'PEN' ? 'S/' : moneda + ' '}${precio}`;
}

export default function MapView({ events }) {
  const mapRef = useRef(null);
  const mapInstance = useRef(null);

  useEffect(() => {
    if (!mapRef.current || mapInstance.current) return;

    async function init() {
      const L = await import('leaflet');
      await import('leaflet/dist/leaflet.css');

      const map = L.map(mapRef.current, {
        center: LIMA_CENTER,
        zoom: 12,
        zoomControl: false,
      });

      L.control.zoom({ position: 'bottomright' }).addTo(map);

      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://carto.com/">CARTO</a>',
        maxZoom: 19,
      }).addTo(map);

      mapInstance.current = map;
    }

    init();
    return () => {
      if (mapInstance.current) {
        mapInstance.current.remove();
        mapInstance.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (!mapInstance.current) return;

    const L = require('leaflet');

    mapInstance.current.eachLayer(layer => {
      if (layer instanceof L.Marker) mapInstance.current.removeLayer(layer);
    });

    const valid = events.filter(e => e.latitud && e.longitud);
    if (!valid.length) return;

    valid.forEach(event => {
      const marker = L.marker([event.latitud, event.longitud]).addTo(mapInstance.current);
      marker.bindPopup(`
        <div class="map-popup">
          <p class="map-popup__title">${event.titulo}</p>
          <p class="map-popup__cat">${event.categoria}</p>
          <p class="map-popup__price">${formatPrice(event.precio, event.moneda)}</p>
        </div>
      `);
    });

    if (valid.length === 1) {
      mapInstance.current.setView([valid[0].latitud, valid[0].longitud], 14);
    } else {
      const bounds = L.latLngBounds(valid.map(e => [e.latitud, e.longitud]));
      mapInstance.current.fitBounds(bounds, { padding: [40, 40] });
    }
  }, [events]);

  return <div ref={mapRef} className="map-container" />;
}
