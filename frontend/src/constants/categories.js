/**
 * Categorías disponibles para filtrar los lugares turísticos.
 * Cada `value` corresponde a un identificador Geoapify válido.
 */
export const CATEGORIES = [
  { value: 'tourism.sights',      label: 'Sitios turísticos', icon: '🏛️' },
  { value: 'tourism.attraction',  label: 'Atracciones',       icon: '🎡' },
  { value: 'catering.restaurant', label: 'Restaurantes',      icon: '🍽️' },
  { value: 'accommodation.hotel', label: 'Hoteles',           icon: '🏨' },
  { value: 'natural',             label: 'Naturaleza',        icon: '🌿' },
  { value: 'entertainment',       label: 'Entretenimiento',   icon: '🎭' },
]

export const DEFAULT_CATEGORY = CATEGORIES[0].value
