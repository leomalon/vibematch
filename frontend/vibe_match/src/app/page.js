"use client";

import { useState,useEffect } from "react";
import ColorBends from '@/Components/ui/Background';
import { ExternalLink,Search,SlidersHorizontal } from "lucide-react";
import CategorySidebar from "@/Components/features/SideBar";


export default function Home() {
  const [query, setQuery] = useState("");
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const resetSearch = () => {
    setQuery("");
    setEvents([]);
    setHasSearched(false);
  };

  const searchEvents = async () => {
    if (!query) return;

    setHasSearched(true);
    setLoading(true);
    setEvents([]);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/events/search`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      const data = await res.json();
      setEvents(data);
    } catch (error) {
      console.error("Error fetching events:", error);
    } finally {
      setLoading(false);
    }
  };
  
  const capitalizeFirst = (text) => {
  if (!text) return "";
  return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
  };

  useEffect(() => {
    const check = () => setIsMobile(window.innerWidth <= 850);
    check(); // run once on mount
    window.addEventListener("resize", check);
    return () => window.removeEventListener("resize", check); // cleanup
  }, []);

  const CATEGORIES = [
    "Arte-cultura",
    "Teatro",
    "Restaurante",
    "Bar",
    "Rooftop",
    "Conciertos",
    "Hotel",
    "Deportes",
    "Viaje-aventura",
    "Paseo",
    "Ocio",
    "Fútbol",
    "Entretenimiento",
    "Cursos-talleres",
    "Seminarios-Conferencias",
    "Stand-up"
  ];


  const styles = {
    page: {
      position: "relative",
      maxHeight: "100vh",
      maxWidth:'100vw',
      color: "white",
      overflow:'hidden'
    },

  background: {
    position: "fixed",
    top: 0,
    left: 0,
    maxWidth:'100vw',
    height:'100vh',
    width:'100vw',
    zIndex: 0,
    pointerEvents: "none",
  },

  // 🔥 Top-left logo
  header: {
    position: "absolute",
    top: "20px",
    zIndex: 2,
    display:"flex",
    width:'100%',
    justifyContent:'space-between',
  },

  logo: {
    fontSize: "24px",
    fontWeight: "600",
    letterSpacing: "1px",
    marginLeft:'15px'
  },

  // Mobile toggle button (top-right)
  mobileToggle: {
    marginRight:'15px',
    zIndex: 101,
    background: "rgba(255,255,255,0.1)",
    backdropFilter: "blur(10px)",
    border: "1px solid rgba(255,255,255,0.2)",
    borderRadius: "50%",
    width: "40px", height: "40px",
    display: "flex",
    alignItems: "center", justifyContent: "center",
    cursor: "pointer",
    color: "white",
  },
  // Overlay behind mobile sidebar
  overlay: {
    position: "fixed",
    inset: 0,
    background: "rgba(0,0,0,0.4)",
    zIndex: 99,
  },

  desktopContainer : {
    position: "fixed",
    top: 100,
    zIndex:800,
    marginLeft:'15px'
  },


  // 🔥 Center container
 centerContainer: (hasSearched) => ({
    position: "fixed",
    marginTop:"35vh",
    marginTop: hasSearched ? "20px" : "35vh",
    display: "flex",
    justifyContent: "center",
    width: "100%",
    zIndex: 2,
    transition: "margin 0.5s ease",
  }),

  // 🔥 Input wrapper (important)
  inputWrapper: {
    position: "relative",
    width: "550px",
    maxWidth: "90%",
  },

  // 🔥 Input styling
  input: {
    width: "100%",
    padding: "14px 110px 14px 40px", // 👈 left padding added
    fontSize: "16px",
    borderRadius: "999px",
    border: "1px solid white",
    background: "white",
    color: "black",
    outline: "none",
  },

  // 🔥 Placeholder styling (subtle UX upgrade)
  inputPlaceholder: {
    color: "#aaa",
  },

  // 🔥 Button INSIDE input
  innerButton: {
    position: "absolute",
    right: "5px",
    top: "50%",
    transform: "translateY(-50%)",
    padding: "8px 16px",
    borderRadius: "999px",
    border: "none",
    background: "white",
    color: "black",
    cursor: "pointer",
    fontWeight: "500",
  },

  resetButton: {
  position: "absolute",
  left: "12px",
  top: "50%",
  transform: "translateY(-50%)",
  background: "transparent",
  border: "none",
  color: "black",
  fontSize: "16px",
  cursor: "pointer",
  opacity: 0.7,
  },

  // Results section
  resultsContainer: {
    position: "relative",
    zIndex: 2,
    padding: "2rem",
    maxWidth: "900px",
    maxHeight:"80vh",
    marginTop:"80px",
    marginLeft: "auto",
    marginRight: "auto",
    overflowY: "auto",
    overflowX: "hidden",
  },

  grid: {
    display: "grid",
    gap: "15px",
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

  cardHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },

  // 🔥 Vibrant title
  title: {
    fontSize: "18px",
    fontWeight: "600",
    color: "#00ffd1", // matches your background palette
    margin: 0,
    textTransform: "uppercase"
  },

  // 🔥 Description
  description: {
    color: "white",
    fontSize: "14px",
    lineHeight: "1.4",
    margin: 0,
    display: "-webkit-box",
    WebkitLineClamp: 3,
    WebkitBoxOrient: "vertical",
    overflow: "hidden"
  },

  // 🔥 Bottom row
  footer: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginTop: "5px",
  },

  category: {
    fontSize: "13px",
    color: "#aaa",
    textTransform: "uppercase"
  },

  price: {
    fontSize: "14px",
    fontWeight: "500",
    color: "white",
  },

  // 🔥 Icon button
  iconButton: {
    background: "transparent",
    border: "1px solid rgba(255,255,255,0.2)",
    borderRadius: "50%",
    padding: "6px",
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    color: "white",
  },

    // 🔥 Loader container (centered)
  loaderContainer: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    marginTop: "40px",
    gap: "10px",
  },

  // 🔥 Spinner
  spinner: {
    width: "40px",
    height: "40px",
    border: "3px solid rgba(255,255,255,0.2)",
    borderTop: "3px solid #00ffd1", // vibrant color
    borderRadius: "50%",
    animation: "spin 1s linear infinite",
  },

  loaderText: {
    color: "white",
    fontSize: "14px",
    opacity: 0.8,
  },
};

return (
  <div style={styles.page}>

    {/* Background */}
    <div style={styles.background}>
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

    {/* Foreground UI */}
    {/* Top bar */}
    <div style={styles.header}>
      <h1 style={styles.logo}>VibeMatch</h1>
      <div style={{position: 'relative', display:'flex' }}>
        {/* Home button */}
      
      {isMobile && (
        <button
          onClick={() => setSidebarOpen(true)}
          style={styles.mobileToggle}
        >
          <SlidersHorizontal size={18} />
        </button>)
      }
      
      </div>


    </div>

    {/* Mobile overlay */}
    {(isMobile && sidebarOpen) && (
      <div style={styles.overlay} onClick={() => setSidebarOpen(false)} />
  
    )}
  
    {/* Mobile sidebar */}
    {(isMobile && sidebarOpen) && (
      
      <div className="sidebar-scroll">
          <CategorySidebar
            CATEGORIES={CATEGORIES}
            isMobile={isMobile}
            selected={selectedCategory}
            isOpen={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
          />
      </div>)
    }


    {/* Desktop sidebar */}
    {!isMobile && 
      (<div style={styles.desktopContainer} className="sidebar-scroll">
        <CategorySidebar
          CATEGORIES={CATEGORIES}
          isMobile={isMobile}
          selected={selectedCategory}
          isOpen={true}
          onClose={() => {}}
        />
      </div>)
    }


    {/* Centered search */}
    <div style={styles.centerContainer(hasSearched)}>
      <div style={styles.inputWrapper}>
        <input
          type="text"
          placeholder="Describe el plan que quieres..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && searchEvents()}
          style={styles.input}
        />

        <button onClick={searchEvents} style={styles.innerButton}>
          <Search size={18} />
        </button>

        {query && (
          <button onClick={resetSearch} style={styles.resetButton}>
            ✕
          </button>
        )}
      </div>
    </div>

    {/* Results */}
    <main style={styles.resultsContainer} className="sidebar-scroll">
      {loading && (
        <div style={styles.loaderContainer}>
          <div style={styles.spinner}></div>
          <p style={styles.loaderText}>Cargando...</p>
        </div>
      )}

    {!loading && hasSearched && events.length === 0 && (
      <p>Lo sentimos, no se han encontrado resultados...</p>
    )}

    <div style={styles.grid}>
      {events.map((event, index) => (
        <div key={index} style={styles.card}>
        {/* Top row: Title + action */}
        <div style={styles.cardHeader}>
          <h3 style={styles.title}>{capitalizeFirst(event.titulo)}</h3>

          <a href={event.url} target="_blank" rel="noopener noreferrer">
            <button style={styles.iconButton}>
              <ExternalLink size={18} />
            </button>
          </a>
        </div>

        {/* Description */}
        <p style={styles.description}>{event.descripcion}</p>

        {/* Footer: category + price */}
        <div style={styles.footer}>
          <span style={styles.category}>{event.categoria}</span>

          <span style={styles.price}>
            {event.precio} {event.moneda}
          </span>
        </div>
      </div>
          ))}
        </div>
    </main>



  </div>

);
}