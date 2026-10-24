import PlaceCard from './PlaceCard'
import Loader from './Loader'
import ErrorAlert from './ErrorAlert'

/**
 * Grid de resultados que orquesta PlaceCard, Loader y ErrorAlert
 * según el estado del fetch.
 *
 * @param {{ data, status, error }} props — retorno de usePlaces()
 */
export default function PlacesGrid({ data, status, error }) {
  return (
    <section className="mt-10" aria-live="polite">
      {/* Encabezado de la sección */}
      <header className="mb-6 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-coffee-900">Lugares cercanos</h2>
          <p className="mt-1 text-sm text-coffee-500">
            Radio de 5 km alrededor del centro de Manizales
          </p>
        </div>

        {status === 'success' && data && (
          <div className="flex flex-wrap items-center gap-3 text-sm">
            <span className="font-medium text-coffee-600">
              {data.count} {data.count === 1 ? 'lugar encontrado' : 'lugares encontrados'} · {data.city}
            </span>
            {data.ai_enriched && (
              <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-50 border border-amber-200 px-3 py-0.5 text-xs font-semibold text-amber-700">
                <span className="h-1.5 w-1.5 rounded-full bg-amber-500 animate-pulse-soft" aria-hidden="true" />
                Ordenado con IA · {data.ai_model}
              </span>
            )}
          </div>
        )}
      </header>

      {/* Estado: cargando */}
      {status === 'loading' && <Loader />}

      {/* Estado: error */}
      {status === 'error' && <ErrorAlert message={error} />}

      {/* Estado: sin resultados */}
      {status === 'success' && data?.places?.length === 0 && (
        <div className="rounded-xl border border-dashed border-coffee-200 bg-coffee-50 px-6 py-12 text-center animate-fade-in">
          <p className="text-lg font-medium text-coffee-600">Sin resultados</p>
          <p className="mt-1 text-sm text-coffee-400">
            No se encontraron lugares para esta categoría en el área seleccionada.
          </p>
        </div>
      )}

      {/* Estado: resultados */}
      {status === 'success' && data?.places?.length > 0 && (
        <>
          <ul className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 list-none p-0 m-0">
            {data.places.map((place, index) => (
              <li
                key={`${place.name}-${place.latitude}-${place.longitude}`}
                className="animate-slide-up"
                style={{ animationDelay: `${index * 60}ms` }}
              >
                <PlaceCard place={place} />
              </li>
            ))}
          </ul>

          {data.fallback_reason && (
            <p className="mt-4 rounded-lg bg-amber-50 border border-amber-200 px-4 py-3 text-sm text-amber-700">
              {data.fallback_reason}
            </p>
          )}
        </>
      )}
    </section>
  )
}
