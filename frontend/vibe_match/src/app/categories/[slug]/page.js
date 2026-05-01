"use client";

import { useEffect, useState, useMemo,use } from "react";
import { ExternalLink} from "lucide-react";

export default function CategoryPage({ params }) {
  
  const { slug } = use(params);
  const [events, setEvents] = useState([]);
  const [filteredEvents, setFilteredEvents] = useState([]);
  const [selectedMoods, setSelectedMoods] = useState([]);
  const [loading, setLoading] = useState(true);

  // Format slug → display name
  const categoryTitle = useMemo(() => {
    if (!slug) return "";
    return slug
      .replace(/\b\w/g, (c) => c.toUpperCase());
  }, [slug]);

  // Fetch events by category
  useEffect(() => {
    const fetchEvents = async () => {
      setLoading(true);

      try {
        const url = `${process.env.NEXT_PUBLIC_API_URL}/events/categories/${slug}`;
        const res = await fetch(`${url}`,
          {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
            }
          }
        );

        const data = await res.json();
        setEvents(data);
        setFilteredEvents(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
  }, [slug]);

  //Extract moods dynamically from events
  const moods = useMemo(() => {
    const set = new Set();

    events.forEach((e) => {
      if (Array.isArray(e.mood)) {
        e.mood.forEach((m) => set.add(m));
      }
    });

    return Array.from(set);
  }, [events]);

  // Handle filter
  const handleMoodFilter = (mood) => {
    setSelectedMoods((prev) => { //prev is the current state as the argument
      if (prev.includes(mood)) {
        // remove
        return prev.filter((m) => m !== mood);
      } else {
        // add
        return [...prev, mood];
      }
    });
  };

  useEffect(() => {
    if (selectedMoods.length === 0) {
      setFilteredEvents(events);
      return;
    }

    const filtered = events.filter((e) =>
      Array.isArray(e.mood) &&
      selectedMoods.every((m) => e.mood.includes(m))
    );

    setFilteredEvents(filtered);
  }, [selectedMoods, events]);

  const styles = {
    container: {
      maxWidth: "900px",
      margin: "0 auto",
      padding: "20px",
      color: "white",
    },

    title: {
      fontSize: "28px",
      fontWeight: "600",
      marginBottom: "20px",
      textTransform: "uppercase",
    },

    filters: {
      display: "flex",
      flexWrap: "wrap",
      gap: "10px",
      marginBottom: "25px",
    },

    pill: (active) => ({
      padding: "8px 14px",
      borderRadius: "999px",
      border: "1px solid rgba(255,255,255,0.2)",
      background: active ? "#00ffd1" : "rgba(255,255,255,0.1)",
      color: active ? "black" : "white",
      cursor: "pointer",
      fontSize: "13px",
      transition: "all 0.2s",
    }),

    grid: {
      display: "grid",
      gap: "15px",
    },
    cardHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    },

    card: {
      background: "rgba(0,0,0,0.6)",
      backdropFilter: "blur(10px)",
      borderRadius: "14px",
      padding: "16px",
      display: "flex",
      flexDirection: "column",
      gap: "10px",
    },

    titleCard: {
      fontSize: "18px",
      fontWeight: "600",
      color: "#00ffd1",
      textTransform: "uppercase",
    },

    description: {
      fontSize: "14px",
      color: "white",
      lineHeight: "1.4",
    },

    footer: {
      display: "flex",
      justifyContent: "space-between",
      fontSize: "13px",
      color: "#aaa",
    },
  };

  return (
    <div style={styles.container}>

      {/* Category Title */}
      <h1 style={styles.title}>{categoryTitle}</h1>

      {/*  Mood Filters */}
      <div style={styles.filters}>
        {moods.map((mood) => (
          <button
            key={mood}
            onClick={() => handleMoodFilter(mood)}
            style={styles.pill(selectedMoods.includes(mood))}
          >
            {mood}
          </button>
        ))}
      </div>

      {/* Loading */}
      {loading && <p>Cargando eventos...</p>}

      {/*  No results */}
      {!loading && filteredEvents.length === 0 && (
        <p>No hay eventos en esta categoría.</p>
      )}

      {/* Events */}
      <div style={styles.grid}>
        {filteredEvents.map((event, i) => (
          <div key={i} style={styles.card}>
            {/* Top row: Title + action */}
            <div style={styles.cardHeader}>
              <h3 style={styles.titleCard}>{event.titulo}</h3>

              <a href={event.url} target="_blank" rel="noopener noreferrer">
                <button style={styles.iconButton}>
                  <ExternalLink size={18} />
                </button>
              </a>
            </div>
            {/* Description */}
            <p style={styles.description}>{event.descripcion}</p>

            <div style={styles.footer}>
              <span>{event.mood?.join("/")}</span>
              <span>
                {event.precio} {event.moneda}
              </span>
            </div>
          </div>
        ))}
      </div>

    </div>
  );
}