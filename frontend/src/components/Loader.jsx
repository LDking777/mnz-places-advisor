/**
 * Spinner de carga con animación pulsante y texto accesible.
 */
export default function Loader({ message = 'Cargando recomendaciones…' }) {
  return (
    <div
      className="flex flex-col items-center justify-center gap-4 py-16 animate-fade-in"
      role="status"
      aria-label={message}
    >
      {/* Spinner con anillos concéntricos */}
      <div className="relative w-12 h-12">
        <div className="absolute inset-0 rounded-full border-3 border-coffee-200" />
        <div className="absolute inset-0 rounded-full border-3 border-transparent border-t-emerald-600 animate-spin-slow" />
      </div>
      <p className="text-sm text-coffee-500 animate-pulse-soft">{message}</p>
    </div>
  )
}
