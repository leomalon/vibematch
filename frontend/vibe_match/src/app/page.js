"use client";
import { useState, useEffect, useCallback, useRef } from "react";
import { Search, List, Map } from "lucide-react";
import CategoryDropdown from "@/Components/features/CategoryDropdown";
import MoodFilter from "@/Components/features/MoodFilter";
import DateFilter from "@/Components/features/DateFilter";
import PriceFilter from "@/Components/features/PriceFilter";
import EventCard from "@/Components/features/EventCard";
import SearchChip from "@/Components/features/SearchChip";
import MapView from "@/Components/features/MapView";
import ColorBends from "@/Components/ui/Background";
import "./page.css";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

function buildListUrl({ category, moodFilter, dateFilter, priceMax }) {
  const params = new URLSearchParams();
  if (category) params.set("categoria", category);
  if (moodFilter) params.set("mood", moodFilter);
  if (dateFilter) params.set("fecha", dateFilter);
  if (priceMax !== undefined && priceMax !== null) params.set("precio_max", String(priceMax));
  return `${API_URL}/events/list?${params.toString()}`;
}

export default function Home() {
  const [events, setEvents] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState(null);
  const [moodFilter, setMoodFilter] = useState(null);
  const [dateFilter, setDateFilter] = useState("hoy");
  const [priceFilter, setPriceFilter] = useState("gratis");
  const [priceMax, setPriceMax] = useState(0);
  const [displayMode, setDisplayMode] = useState("list");
  const [loading, setLoading] = useState(false);
  const [searching, setSearching] = useState(false);
  const cardsRef = useRef(null);

  const fetchEvents = useCallback(async () => {
    setLoading(true);
    try {
      const url = buildListUrl({ category, moodFilter, dateFilter, priceMax });
      const res = await fetch(url);
      const data = await res.json();
      setEvents(data);
    } catch (err) {
      console.error("Error fetching events:", err);
    } finally {
      setLoading(false);
    }
  }, [category, moodFilter, dateFilter, priceMax]);

  useEffect(() => {
    if (!searching) fetchEvents();
  }, [fetchEvents, searching]);

  async function handleSearch() {
    if (!query.trim()) return;
    setSearching(true);
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/events/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: query.trim() }),
      });
      const data = await res.json();
      setSearchResults(data);
    } catch (err) {
      console.error("Search error:", err);
    } finally {
      setLoading(false);
    }
  }

  function clearSearch() {
    setQuery("");
    setSearchResults([]);
    setSearching(false);
  }

  function handleCategorySelect(slug) {
    setCategory(slug);
    setMoodFilter(null);
    setSearching(false);
    setQuery("");
    setSearchResults([]);
  }

  function handleMoodSelect(slug) {
    setMoodFilter(slug);
    setSearching(false);
    setQuery("");
    setSearchResults([]);
  }

  function handleDateChange(val) {
    setDateFilter(val);
  }

  function handlePriceChange(key, max, min) {
    setPriceFilter(key);
    setPriceMax(max !== undefined ? max : undefined);
  }

  const title = (() => {
    if (searching) return "Resultados para tu búsqueda";
    if (category) {
      const label = category.charAt(0).toUpperCase() + category.slice(1).replace(/-/g, " ");
      const prefix = dateFilter === "hoy" ? "Hoy en" : dateFilter === "manana" ? "Mañana en" : "En";
      return `${prefix} ${label}`;
    }
    return dateFilter === "manana" ? "Mañana en VibeMatch" : "Hoy en VibeMatch";
  })();

  const displayEvents = searching ? searchResults : events;
  const eventCount = displayEvents.length;

  return (
    <div className="page">
      {/* Background */}
      <div className="background-colorbends">
        <ColorBends
          colors={["#ff5c7a", "#8a5cff", "#00ffd1"]}
          rotation={0}
          speed={0.5}
          scale={1}
          frequency={1}
          warpStrength={1}
          mouseInfluence={1}
          parallax={1}
          noise={0.4}
          transparent
          autoRotate={1}
        />
      </div>
      {/* ── Header ── */}
      <header className="header">
        <div className="header__left">
          <span className="header__logo">VibeMatch</span>
          <CategoryDropdown selected={category} onSelect={handleCategorySelect} />
          <MoodFilter selected={moodFilter} onSelect={handleMoodSelect} />
        </div>

        <div className="header__right">
          <div className="view-toggle">
            <button
              className={`view-toggle__btn ${displayMode === "list" ? "view-toggle__btn--active" : ""}`}
              onClick={() => setDisplayMode("list")}
            >
              <List size={15} /> Lista
            </button>
            <button
              className={`view-toggle__btn ${displayMode === "map" ? "view-toggle__btn--active" : ""}`}
              onClick={() => setDisplayMode("map")}
            >
              <Map size={15} /> Mapa
            </button>
          </div>
        </div>
      </header>

      {/* ── Search ── */}
      <div className="search-area">
        <div className="search-input-wrap">
          <input
            className="search-input"
            type="text"
            placeholder="Describe el plan que quieres..."
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleSearch()}
          />
          <button className="search-btn" onClick={handleSearch}>
            <Search size={20} />
          </button>
        </div>
      </div>

      {/* ── Filters (hidden during search) ── */}
      {!searching && (
        <div className="filters-row">
          <DateFilter value={dateFilter} onChange={handleDateChange} />
          <div className="filter-divider" />
          <PriceFilter value={priceFilter} onChange={handlePriceChange} />
        </div>
      )}

      {/* ── Search chip ── */}
      {searching && (
        <div style={{ position: "relative", zIndex: 1, maxWidth: 1100, margin: "20px auto 0", padding: "0 24px" }}>
          <SearchChip query={query} onClear={clearSearch} />
        </div>
      )}

      {/* ── Section title ── */}
      {!loading && (
        <div className="section-header">
          <h2 className="section-title">{title}</h2>
          <span className="section-count">{eventCount} planes</span>
        </div>
      )}

      {/* ── Loading ── */}
      {loading && (
        <div className="loading-wrap">
          <div className="spinner" />
          <p>Cargando eventos...</p>
        </div>
      )}

      {/* ── Content: List or Map ── */}
      {!loading && displayMode === "list" && (
        <div className="cards-scroll" ref={cardsRef}>
          {displayEvents.length === 0 && (
            <p className="empty-msg" style={{ width: "100%" }}>
              No se encontraron eventos con estos filtros.
            </p>
          )}
          {displayEvents.map((event, i) => (
            <EventCard key={event.url || i} event={event} />
          ))}
        </div>
      )}

      {!loading && displayMode === "map" && (
        <div style={{ position: "relative", zIndex: 1, maxWidth: 1100, margin: "0 auto", padding: "0 24px 40px" }}>
          <MapView events={displayEvents} />
        </div>
      )}
    </div>
  );
}
