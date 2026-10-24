/**
 * Tarjeta compacta de un lugar sugerido por el asistente IA.
 *
 * @param {{ name, category, latitude, longitude, reason }} place
 */
export default function ChatSuggestionCard({ place }) {
  const hasCoords = place.latitude != null && place.longitude != null

  return (
    <article className="flex flex-col gap-2 rounded-xl border border-coffee-200 bg-white p-4 transition-all duration-200 hover:border-emerald-300 hover:shadow-md hover:shadow-emerald-900/5">
      {/* Badge */}
      {place.category && (
        <span className="inline-flex self-start rounded-full bg-emerald-50 px-2.5 py-0.5 text-[11px] font-semibold uppercase tracking-wide text-emerald-700">
          {place.category}
        </span>
      )}

      {/* Nombre */}
      <h4 className="text-sm font-semibold text-coffee-900 leading-snug">
        {place.name}
      </h4>

      {/* Razón */}
      {place.reason && (
        <p className="text-xs leading-relaxed text-coffee-500">{place.reason}</p>
      )}

      {/* Link a mapa */}
      {hasCoords && (
        <a
          className="mt-auto inline-flex items-center gap-1 text-xs font-semibold text-emerald-700 no-underline transition-colors hover:text-emerald-500"
          href={`https://www.google.com/maps?q=${place.latitude},${place.longitude}`}
          target="_blank"
          rel="noreferrer"
          aria-label={`Ver ${place.name} en Google Maps`}
        >
          Ver en Google Maps
          <span aria-hidden="true">→</span>
        </a>
      )}
    </article>
  )
}
