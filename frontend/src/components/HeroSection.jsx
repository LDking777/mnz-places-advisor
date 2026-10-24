import CategoryFilter from './CategoryFilter'

/**
 * Hero section con título, descripción y filtros de categoría.
 *
 * @param {string}   category — categoría seleccionada.
 * @param {function} onCategoryChange — callback al cambiar la categoría.
 */
export default function HeroSection({ category, onCategoryChange }) {
  return (
    <header className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-emerald-800 via-emerald-700 to-emerald-900 px-6 py-12 sm:px-10 sm:py-16 lg:px-14 lg:py-20">
      {/* Patrón decorativo de fondo */}
      <div className="pointer-events-none absolute inset-0 opacity-10" aria-hidden="true">
        <div className="absolute -top-20 -right-20 h-80 w-80 rounded-full bg-amber-400 blur-3xl" />
        <div className="absolute -bottom-24 -left-16 h-72 w-72 rounded-full bg-emerald-300 blur-3xl" />
      </div>

      <div className="relative z-10 max-w-2xl">
        {/* Eyebrow */}
        <span className="inline-flex items-center gap-2 rounded-full bg-white/15 px-3 py-1 text-xs font-semibold uppercase tracking-widest text-emerald-100 backdrop-blur-sm">
          <span aria-hidden="true">☕</span>
          Manizales · Caldas
        </span>

        {/* Título */}
        <h1 className="mt-5 text-3xl font-bold leading-tight tracking-tight text-white sm:text-4xl lg:text-5xl">
          Descubre Manizales<br className="hidden sm:block" /> con un guía inteligente
        </h1>

        {/* Descripción */}
        <p className="mt-4 max-w-xl text-base leading-relaxed text-emerald-100/80 sm:text-lg">
          Recomendaciones turísticas curadas desde Geoapify y enriquecidas con IA
          para crear planes a medida, con grounding exclusivo en lugares reales
          del centro de Manizales.
        </p>

        {/* Filtros */}
        <div className="mt-8">
          <p className="mb-3 text-sm font-medium text-emerald-200">
            Explora por categoría
          </p>
          <CategoryFilter value={category} onChange={onCategoryChange} />
        </div>
      </div>
    </header>
  )
}
