import ChatSuggestionCard from './ChatSuggestionCard'
import ErrorAlert from './ErrorAlert'

/**
 * Panel del asistente turístico con IA.
 * Incluye formulario, respuesta y sugerencias de lugares.
 *
 * @param {{ question, setQuestion, response, loading, error, submit }} props — retorno de useChat()
 */
export default function ChatPanel({ question, setQuestion, response, loading, error, submit }) {
  return (
    <section
      className="mt-12 overflow-hidden rounded-2xl border border-coffee-200 bg-white shadow-xl shadow-coffee-900/5"
      aria-live="polite"
    >
      {/* Header */}
      <header className="flex flex-col gap-4 bg-gradient-to-r from-coffee-100 via-coffee-50 to-emerald-50 px-6 py-8 sm:flex-row sm:items-center sm:justify-between sm:px-8">
        <div>
          <span className="inline-flex items-center gap-1.5 text-xs font-semibold uppercase tracking-widest text-emerald-700">
            <span aria-hidden="true">🤖</span>
            Asistente turístico
          </span>
          <h2 className="mt-2 text-xl font-bold text-coffee-900 sm:text-2xl">
            Pregúntale al guía de Manizales
          </h2>
          <p className="mt-2 max-w-lg text-sm text-coffee-500 leading-relaxed">
            Dime el plan que buscas: tarde lluviosa, ruta fotográfica, paseo
            cultural, comida cercana… y te armo un itinerario usando solo lugares
            reales del mapa.
          </p>
        </div>
        <span className="inline-flex items-center gap-1.5 self-start rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse-soft" aria-hidden="true" />
          Grounding estricto con Geoapify
        </span>
      </header>

      {/* Body */}
      <div className="px-6 py-6 sm:px-8">
        {/* Formulario */}
        <form className="flex flex-col gap-3 sm:flex-row" onSubmit={submit}>
          <label htmlFor="chat-question" className="sr-only">
            Tu pregunta sobre Manizales
          </label>
          <input
            id="chat-question"
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="¿Qué te gustaría hacer hoy en Manizales?"
            maxLength={400}
            disabled={loading}
            className="flex-1 rounded-full border border-coffee-200 bg-coffee-50 px-5 py-3 text-sm text-coffee-900 placeholder:text-coffee-400 transition-colors focus:border-emerald-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500/20 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={loading || !question.trim()}
            className="inline-flex items-center justify-center gap-2 rounded-full bg-emerald-600 px-6 py-3 text-sm font-semibold text-white shadow-md shadow-emerald-600/20 transition-all duration-200 hover:bg-emerald-700 hover:shadow-lg hover:shadow-emerald-600/30 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-emerald-600 disabled:hover:shadow-md cursor-pointer"
          >
            {loading ? (
              <>
                <span className="h-4 w-4 rounded-full border-2 border-white/30 border-t-white animate-spin-slow" aria-hidden="true" />
                Generando plan…
              </>
            ) : (
              'Preguntar al asistente →'
            )}
          </button>
        </form>

        {/* Error */}
        {error && (
          <div className="mt-4">
            <ErrorAlert title="Error del asistente" message={error} />
          </div>
        )}

        {/* Respuesta */}
        {response && (
          <div className="mt-6 space-y-6 animate-slide-up">
            {/* Texto de respuesta */}
            <article className="rounded-xl bg-emerald-50 border border-emerald-200 p-5">
              <header className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between mb-3">
                <div>
                  <p className="text-sm font-semibold text-coffee-900">Respuesta del guía</p>
                  <p className="text-xs text-coffee-500">Basada únicamente en los lugares disponibles</p>
                </div>
                {response.ai_enriched && (
                  <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-50 border border-amber-200 px-3 py-0.5 text-xs font-semibold text-amber-700">
                    <span className="h-1.5 w-1.5 rounded-full bg-amber-500 animate-pulse-soft" aria-hidden="true" />
                    {response.ai_model}
                  </span>
                )}
              </header>
              <p className="whitespace-pre-wrap text-sm leading-relaxed text-coffee-700">
                {response.answer}
              </p>
              {response.fallback_reason && (
                <p className="mt-3 rounded-lg bg-amber-50 border border-amber-200 px-3 py-2 text-xs text-amber-700">
                  {response.fallback_reason}
                </p>
              )}
            </article>

            {/* Lugares sugeridos */}
            {response.suggested_places?.length > 0 && (
              <div>
                <div className="mb-3">
                  <p className="text-sm font-semibold text-coffee-900">
                    Lugares sugeridos para este plan
                  </p>
                  <p className="text-xs text-coffee-500">Listos para abrir en el mapa</p>
                </div>
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                  {response.suggested_places.map((place) => (
                    <ChatSuggestionCard
                      key={`${place.name}-${place.latitude}-${place.longitude}`}
                      place={place}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  )
}
