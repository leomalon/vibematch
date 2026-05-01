"use client";

import { useEffect, useState } from "react";
import { usePathname,useRouter } from "next/navigation";
import CategorySidebar from "@/Components/features/SideBar";
import ColorBends from "@/Components/ui/Background";
import {Home, SlidersHorizontal } from "lucide-react";

export default function CategoriesLayout({ children }) {
  const [isMobile, setIsMobile] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Extract slug from URL
  const pathname = usePathname();
  const currentSlug = pathname.split("/")[2] || null;

  const router = useRouter();

  useEffect(() => {
    const check = () => setIsMobile(window.innerWidth <= 850);
    check();
    window.addEventListener("resize", check);
    return () => window.removeEventListener("resize", check);
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
      minHeight: "100vh",
      color: "white",
      overflowX: "hidden",
    },

    background: {
      position: "fixed",
      inset: 0,
      zIndex: 0,
      pointerEvents: "none",
    },

    header: {
      position: "absolute",
      top: "20px",
      width: "100%",
      display: "flex",
      justifyContent: "space-between",
      zIndex: 10,
      padding: "0 15px",
    },

    logo: {
      fontSize: "24px",
      fontWeight: "600",
    },

    homeButton: {
      display: "flex",
      alignItems: "center",
      gap: "6px",
      padding: "6px 12px",
      borderRadius: "999px",
      background: "rgba(255,255,255,0.08)",
      backdropFilter: "blur(10px)",
      border: "1px solid rgba(255,255,255,0.15)",
      color: "white",
      fontSize: "13px",
      cursor: "pointer",
      transition: "all 0.2s ease",
    },

    mobileToggle: {
      zIndex: 101,
      background: "rgba(255,255,255,0.1)",
      backdropFilter: "blur(10px)",
      border: "1px solid rgba(255,255,255,0.2)",
      borderRadius: "50%",
      width: "40px",
      height: "40px",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      cursor: "pointer",
      color: "white",
    },

    overlay: {
      position: "fixed",
      inset: 0,
      background: "rgba(0,0,0,0.4)",
      zIndex: 99,
    },

    container: {
      display: "flex",
      gap: "20px",
      paddingTop: "80px",
      paddingLeft: "15px",
      paddingRight: "15px",
      position: "relative",
      zIndex: 2,
    },

    content: {
      flex: 1,
    },

    desktopSidebar: {
      position: "sticky",
      top: "80px",
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

      {/* Header */}
      <div style={styles.header}>
        <h1 style={styles.logo}>VibeMatch</h1>

        <div style={{position: 'relative', display:'flex',gap: "10px" }}>
        {/* Home button */}

        <button
          onClick={() => router.push("/")}
          style={styles.homeButton}
        >
          <Home size={16} />
        </button>
          
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
      {isMobile && sidebarOpen && (
        <div
          style={styles.overlay}
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Mobile sidebar */}
      {(isMobile && sidebarOpen) && (
        
        <div className="sidebar-scroll">
          <CategorySidebar
            CATEGORIES={CATEGORIES}
            isMobile={true}
            selected={currentSlug}
            isOpen={true}
            onClose={() => setSidebarOpen(false)}
          />
        </div>
      )}

      {/* Main layout */}
      <div style={styles.container}>

        {/* Desktop sidebar */}
        {!isMobile && (
          <div style={styles.desktopSidebar} className="sidebar-scroll">
            <CategorySidebar
              CATEGORIES={CATEGORIES}
              isMobile={false}
              selected={currentSlug}
              isOpen={false}
              onClose={() => {}}
            />
          </div>
        )}

        {/* Page content */}
        <div style={styles.content}>
          {children}
        </div>

      </div>
    </div>
  );
}