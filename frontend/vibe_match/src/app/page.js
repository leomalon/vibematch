"use client";
import { useState, useEffect, useCallback, useRef } from "react";
import { Search, List, Map } from "lucide-react";
import dynamic from 'next/dynamic';
import "./page.css";

const CategoryDropdown = dynamic(() => import("@/Components/features/CategoryDropdown"), { ssr: false });
const MoodFilter = dynamic(() => import("@/Components/features/MoodFilter"), { ssr: false });
const DateFilter = dynamic(() => import("@/Components/features/DateFilter"), { ssr: false });
const PriceFilter = dynamic(() => import("@/Components/features/PriceFilter"), { ssr: false });
const EventCard = dynamic(() => import("@/Components/features/EventCard"), { ssr: false });
const SearchChip = dynamic(() => import("@/Components/features/SearchChip"), { ssr: false });
const MapView = dynamic(() => import("@/Components/features/MapView"), { ssr: false });
const ColorBends = dynamic(() => import("@/Components/ui/Background"), { ssr: false });

const API_URL = process.env.NEXT_PUBLIC_API_URL;

function buildListUrl({ category, moodFilter, dateFilter, priceMin, priceMax }) {
  const params = new URLSearchParams();
  if (category) params.set("categoria", category);
  if (moodFilter && Array.isArray(moodFilter) && moodFilter.length > 0) {
    moodFilter.forEach(m => params.append("mood", m));
  } else if (moodFilter && typeof moodFilter === 'string') {
    params.set("mood", moodFilter);
  }
  if (dateFilter) params.set("fecha", dateFilter);
  if (priceMin !== undefined && priceMin !== null) params.set("precio_min", String(priceMin));
  if (priceMax !== undefined && priceMax !== null) params.set("precio_max", String(priceMax));
  return `${API_URL}/events/list?${params.toString()}`;
}

export default function Home() {
  const [events, setEvents] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState(null);
  const [moodFilter, setMoodFilter] = useState(null); // null or array of slugs
  const [dateFilter, setDateFilter] = useState("hoy");
  const [priceFilter, setPriceFilter] = useState("gratis");
  const [priceMin, setPriceMin] = useState(undefined);
  const [priceMax, setPriceMax] = useState(0);
  const [displayMode, setDisplayMode] = useState("list");
  const [loading, setLoading] = useState(false);
  const [searching, setSearching] = useState(false);
  const cardsRef = useRef(null);

  const fetchEvents = useCallback(async () => {
    setLoading(true);
    try {
      const url = buildListUrl({ category, moodFilter, dateFilter, priceMin, priceMax });
      const res = await fetch(url);
      const data = await res.json();
      setEvents(data);
    } catch (err) {
      console.error("Error fetching events:", err);
    } finally {
      setLoading(false);
    }
  }, [category, moodFilter, dateFilter, priceMin, priceMax]);

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

  function handleMoodSelect(selectedMoods) {
    setMoodFilter(selectedMoods);
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
    setPriceMin(min !== undefined ? min : undefined);
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

      {/* ── Main Content ── */}
      <main className="main-content">
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
          <div style={{ marginBottom: "16px" }}>
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
          <div className="cards-grid" ref={cardsRef}>
            {displayEvents.length === 0 && (
              <p className="empty-msg" style={{ width: "100%", gridColumn: "1 / -1", textAlign: "center" }}>
                No se encontraron eventos con estos filtros.
              </p>
            )}
            {displayEvents.map((event, i) => (
              <EventCard key={event.url || i} event={event} />
            ))}
          </div>
        )}

        {!loading && displayMode === "map" && (
          <div style={{ position: "relative", zIndex: 1, width: "100%" }}>
            <MapView events={displayEvents} />
          </div>
        )}
      </main>
    </div>
  );
}
