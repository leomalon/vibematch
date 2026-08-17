// Mapping de categorías a nombres de archivo de imagen
// Coloca tus imágenes PNG/SVG en: public/images/categories/
// Nombralas usando el slug de la categoría (ej: arte-cultura.png, restaurante.svg, etc.)

export const CATEGORY_IMAGES = {
  // Eventos / Cultura
  'arte-cultura': 'arte-cultura.png',
  'teatro': 'teatro.png',
  'conciertos': 'conciertos.png',
  'entretenimiento': 'entretenimiento.png',
  'stand-up': 'stand-up.png',
  'cine': 'cine.png',
  'danza': 'danza.png',
  'exposicion': 'exposicion.png',
  'feria': 'feria.png',
  'museo': 'museo.png',
  'musica': 'musica.png',
  'fiesta': 'fiesta.png',
  'festivales': 'festivales.png',

  // Comida / Bebida
  'bar': 'bar.png',
  'restaurante': 'restaurante.png',
  'huarique': 'huarique.png',
  'heladeria': 'heladeria.png',
  'cafeteria': 'cafeteria.png',
  'rooftop': 'rooftop.png',

  // Actividades
  'playa': 'playa.png',
  'hotel': 'hotel.png',
  'deportes': 'deportes.png',
  'futbol': 'futbol.png',
  'viaje-aventura': 'viaje-aventura.png',
  'paseo': 'paseo.png',
  'ocio': 'ocio.png',

  // Educativos
  'cursos-talleres': 'cursos-talleres.png',
  'seminarios-conferencias': 'seminarios-conferencias.png',

  // Fallback
  'default': 'default.png',
};

export function getCategoryImage(category) {
  if (!category) return `/images/categories/${CATEGORY_IMAGES.default}`;
  const slug = category
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/\s+/g, '-');
  const filename = CATEGORY_IMAGES[slug] || CATEGORY_IMAGES.default;
  return `/images/categories/${filename}`;
}