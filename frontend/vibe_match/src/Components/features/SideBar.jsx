import {  X } from "lucide-react";
import { useRouter } from "next/navigation";

export default function CategorySidebar({ CATEGORIES, isMobile, selected, isOpen, onClose }) {
  const desktopSideBarStyle = {
    width: "200px",
    height:'550px',
    flexShrink: 0, //Prevents the sidebar from shrinking inside a flex container.
    background: "rgba(255,255,255,0.08)",
    backdropFilter: "blur(16px)",
    WebkitBackdropFilter: "blur(16px)",
    border: "1px solid rgba(255,255,255,0.18)",
    borderRadius: "16px",
    padding: "20px 14px",
    display: "flex",
    flexDirection: "column",
    gap: "4px",
    alignSelf: "flex-start",
    position: "sticky",
    top: "20px",
    overflowY: "auto",
    overflowX: "hidden"
  };

  const mobileSidebarStyle = {
    position: "fixed",
    top: 0,
    right: 0,
    maxheight: "100vh",
    width: "240px",
    background: isMobile ? "rgba(10,10,20,0.65)":'transparent',
    backdropFilter: "blur(20px)",
    WebkitBackdropFilter: "blur(20px)",
    border: "1px solid rgba(255,255,255,0.18)",
    borderLeft: "1px solid rgba(255,255,255,0.18)",
    borderRadius: "16px 0 0 16px",
    padding: "24px 16px",
    display: "flex",
    flexDirection: "column",
    gap: "4px",
    zIndex: 100,
    transform: isOpen ? "translateX(0)" : "translateX(100%)",
    transition: "transform 0.3s ease",
    overflowY: "auto",
    overflowX: "hidden"
  };

  const router = useRouter();

  const toSlug = (text) =>
    text
    .toLowerCase()
    .normalize("NFD") //Decompose accented characters into base + diacritic
    .replace(/[\u0300-\u036f]/g, "") //Remove accents
    .replace(/\s+/g, "-");//Replace whitespace with hyphens

  return (
    <div style={isMobile ? mobileSidebarStyle : desktopSideBarStyle}>
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: "12px",
      }}>
        <span style={{
          fontSize: "11px",
          fontWeight: "600",
          letterSpacing: "1.5px",
          color: "rgba(255,255,255,0.5)",
          textTransform: "uppercase",
        }}>
          Categoría
        </span>
        {isMobile && (
          <button onClick={onClose} style={{
            background: "transparent",
            border: "none",
            color: "rgba(255,255,255,0.6)",
            cursor: "pointer",
            padding: "2px",
          }}>
            <X size={16} />
          </button>
        )}
      </div>

      {CATEGORIES.map((cat) => (
        <button
          key={cat}
          onClick={() => {
            const slug = toSlug(cat)

            router.push(`/categories/${slug}`);

            if (isMobile) onClose();
          }}
          style={{
            padding: "8px 10px",
            borderRadius: "8px",
            background: selected === toSlug(cat) ? "rgba(0,255,209,0.15)" : "transparent",
            border: "none",
            color: selected === toSlug(cat) ? "#00ffd1" : "rgba(255,255,255,0.8)",
            fontWeight: selected === toSlug(cat) ? "500" : "400",
            fontSize: "14px",
            textAlign: "left",
            cursor: "pointer",
            transition: "background 0.2s, color 0.2s",
          }}
        >
          {cat}
        </button>
      ))}
    </div>
  );
}