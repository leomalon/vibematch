'use client';
import { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './MapView.css';

const LIMA_CENTER = [-12.05, -77.04];

function formatPrice(precio, moneda) {
  if (precio === null || precio === undefined) return '';
  if (precio === 0) return 'Gratis';
  return `${moneda === 'PEN' ? 'S/' : moneda + ' '}${precio}`;
}

/* ── Custom icons (no default marker image needed) ── */

const eventIcon = L.divIcon({
  className: 'map-event-marker',
  html: '<div class="map-event-pin"></div>',
  iconSize: [14, 14],
  iconAnchor: [7, 7],
  popupAnchor: [0, -10],
});

const userIcon = L.divIcon({
  className: 'map-user-marker',
  html: '<div class="map-user-dot"><div class="map-user-pulse"></div></div>',
  iconSize: [20, 20],
  iconAnchor: [10, 10],
});

function buildPopup(event) {
  const moods = (event.mood || [])
    .map(m => `<span class="map-popup__mood">${m}</span>`)
    .join('');

  return `
    <div class="map-popup">
      <p class="map-popup__title">${event.titulo}</p>
      <p class="map-popup__cat">${event.categoria}</p>
      ${event.direccion ? `<p class="map-popup__addr">${event.direccion}</p>` : ''}
      ${moods ? `<div class="map-popup__moods">${moods}</div>` : ''}
      <p class="map-popup__price">${formatPrice(event.precio, event.moneda)}</p>
    </div>
  `;
}

export default function MapView({ events }) {
  const mapRef = useRef(null);
  const mapInstance = useRef(null);
  const markersRef = useRef([]);
  const userMarkerRef = useRef(null);
  const [userLocation, setUserLocation] = useState(null);

  useEffect(() => {
    if (typeof window === 'undefined' || !navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition(
      (pos) => setUserLocation([pos.coords.latitude, pos.coords.longitude]),
      () => {},
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 30000 }
    );
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined' || !mapRef.current || mapInstance.current) return;
    const map = L.map(mapRef.current, { center: LIMA_CENTER, zoom: 12, zoomControl: false });
    L.control.zoom({ position: 'bottomright' }).addTo(map);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; CARTO',
      maxZoom: 19,
    }).addTo(map);
    mapInstance.current = map;
    return () => { map.remove(); mapInstance.current = null; };
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined' || !mapInstance.current) return;
    const t = setTimeout(() => mapInstance.current.invalidateSize(), 100);
    return () => clearTimeout(t);
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const map = mapInstance.current;
    if (!map || !userLocation) return;
    if (userMarkerRef.current) map.removeLayer(userMarkerRef.current);
    userMarkerRef.current = L.marker(userLocation, { icon: userIcon, zIndexOffset: 1000 })
      .addTo(map)
      .bindPopup('<div class="map-popup"><p class="map-popup__title">📍 Tu ubicación</p></div>');
    map.flyTo(userLocation, 14, { duration: 1.5 });
  }, [userLocation]);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const map = mapInstance.current;
    if (!map) return;
    setTimeout(() => map.invalidateSize(), 150);

    markersRef.current.forEach(m => map.removeLayer(m));
    markersRef.current = [];

    const valid = events.filter(e => e.latitud && e.longitud);
    if (!valid.length) return;

    valid.forEach(event => {
      const marker = L.marker([event.latitud, event.longitud], { icon: eventIcon }).addTo(map);
      marker.bindPopup(buildPopup(event));
      markersRef.current.push(marker);
    });

    const allPoints = [...valid.map(e => [e.latitud, e.longitud])];
    if (userLocation) allPoints.push(userLocation);
    if (allPoints.length > 1) {
      map.fitBounds(L.latLngBounds(allPoints), { padding: [50, 50] });
    } else if (allPoints.length === 1) {
      map.setView(allPoints[0], 14);
    }
  }, [events]);

  return <div ref={mapRef} className="map-container" />;
}
