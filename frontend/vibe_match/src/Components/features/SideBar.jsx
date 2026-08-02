import {  X } from "lucide-react";
import { useRouter } from "next/navigation";
import "@/Components/features/SideBar.css";

export default function CategorySidebar({ CATEGORIES, isMobile, selected, isOpen, onClose }) {

  const router = useRouter();

  const toSlug = (text) =>
    text
    .toLowerCase()
    .normalize("NFD") //Decompose accented characters into base + diacritic
    .replace(/[\u0300-\u036f]/g, "") //Remove accents
    .replace(/\s+/g, "-");//Replace whitespace with hyphens

  return (
    <div className={`${isMobile ? "mobileSidebarStyle" : "desktopSidebarStyle"} sidebar-scroll`}>
        {isMobile && (
          <button onClick={onClose} className="mobileCloseButton">
            <X size={16} />
          </button>
        )}

      {CATEGORIES.map((cat) => (
        <button
          key={cat}
          onClick={() => {
            const slug = toSlug(cat)

            router.push(`/categories/${slug}`);

            if (isMobile) onClose();
          }}
          className={`button-category ${selected === toSlug(cat) ? "buttonCategorySelected" : "buttonCategoryOption"}`}
        >
          {cat}
        </button>
      ))}
    </div>
  );
}