/**
 * Alerta de error reutilizable con diseño accesible.
 */
export default function ErrorAlert({ title = 'No se pudieron cargar los lugares', message }) {
  return (
    <div
      className="flex items-start gap-3 rounded-xl border border-terra-500/20 bg-terra-50 px-5 py-4 animate-fade-in"
      role="alert"
    >
      {/* Ícono de advertencia */}
      <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-terra-500/15 text-terra-600 text-sm" aria-hidden="true">
        !
      </span>
      <div className="min-w-0">
        <p className="font-semibold text-terra-700">{title}</p>
        {message && (
          <p className="mt-1 text-sm text-terra-600/80 break-words">{message}</p>
        )}
      </div>
    </div>
  )
}
