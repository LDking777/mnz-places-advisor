/**
 * Tarjeta individual de un lugar turístico.
 * Componente puro: recibe datos y renderiza.
 *
 * @param {{ name, category, latitude, longitude, reason }} place
 */
export default function PlaceCard({ place }) {
  const mapsUrl = `https://www.google.com/maps?q=${place.latitude},${place.longitude}`

  return (
    <article className="group flex flex-col gap-3 rounded-xl border border-coffee-200 bg-white p-5 transition-all duration-200 hover:-translate-y-1 hover:shadow-lg hover:shadow-coffee-900/8 hover:border-emerald-300">
      {/* Badge de categoría */}
      <span className="inline-flex self-start rounded-full bg-emerald-50 px-3 py-0.5 text-xs font-semibold uppercase tracking-wide text-emerald-700">
        {place.category}
      </span>

      {/* Nombre */}
      <h3 className="text-lg font-semibold leading-snug text-coffee-900">
        {place.name}
      </h3>

      {/* Razón IA (opcional) */}
      {place.reason && (
        <p className="text-sm leading-relaxed text-coffee-500">
          {place.reason}
        </p>
      )}

      {/* Coordenadas */}
      <div className="flex items-center gap-2 font-mono text-xs text-coffee-400">
        <span>Lat {place.latitude.toFixed(5)}</span>
        <span aria-hidden="true">·</span>
        <span>Lng {place.longitude.toFixed(5)}</span>
      </div>

      {/* Link a Google Maps */}
      <a
        className="mt-auto inline-flex items-center gap-1 text-sm font-semibold text-emerald-700 no-underline transition-colors hover:text-emerald-500"
        href={mapsUrl}
        target="_blank"
        rel="noreferrer"
        aria-label={`Ver ${place.name} en Google Maps`}
      >
        Ver en Google Maps
        <span className="transition-transform group-hover:translate-x-0.5" aria-hidden="true">→</span>
      </a>
    </article>
  )
}
