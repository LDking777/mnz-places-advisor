/**
 * Capa de servicios — toda comunicación con la API REST pasa por aquí.
 *
 * La URL base se inyecta mediante variable de entorno:
 *   - DEV:  .env.development  → http://localhost:8000
 *   - QA:   .env.qa           → https://qa-api.manizales-tours.example.com
 *   - PROD: .env.production   → https://api.manizales-tours.example.com
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

const REQUEST_TIMEOUT_MS = 10_000

/**
 * Construye una URL completa a partir de un path relativo y parámetros opcionales.
 * Lanza si VITE_API_BASE_URL no está configurada.
 */
function buildUrl(path, params = {}) {
  if (!API_BASE_URL) {
    throw new Error(
      'VITE_API_BASE_URL no está configurada. Revise el archivo .env para este entorno.',
    )
  }

  const url = new URL(path, API_BASE_URL)
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') {
      url.searchParams.set(key, String(value))
    }
  }
  return url
}

/**
 * Wrapper de fetch con timeout y manejo estandarizado de errores.
 */
async function request(url, options = {}) {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)

  // Propagar abort externo al controller interno
  const externalSignal = options.signal
  const onExternalAbort = () => controller.abort()
  externalSignal?.addEventListener('abort', onExternalAbort, { once: true })

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        Accept: 'application/json',
        ...options.headers,
      },
      signal: controller.signal,
    })

    const payload = await response.json().catch(() => null)

    if (!response.ok) {
      const message =
        payload?.error?.message ??
        payload?.detail ??
        `El backend respondió con estado ${response.status}.`
      throw new Error(message)
    }

    return payload
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('La solicitud tardó demasiado o fue cancelada.')
    }
    throw error
  } finally {
    clearTimeout(timeoutId)
    externalSignal?.removeEventListener('abort', onExternalAbort)
  }
}

/* ═══════════════════════════════════════════════
 *  Endpoints públicos
 * ═══════════════════════════════════════════════ */

/**
 * GET /api/v1/places/recommendations
 * Obtiene lugares turísticos filtrados por categoría.
 */
export async function fetchRecommendations({ category = 'tourism.sights', signal } = {}) {
  const url = buildUrl('/api/v1/places/recommendations', { category })
  const payload = await request(url, { signal })

  if (!payload || !Array.isArray(payload.places)) {
    throw new Error('El backend devolvió una estructura de datos inesperada.')
  }

  return payload
}

/**
 * POST /api/v1/chat/assistant
 * Envía una pregunta al asistente turístico con IA.
 */
export async function askAssistant({ question, category, limit = 12, signal } = {}) {
  const url = buildUrl('/api/v1/chat/assistant')

  const payload = await request(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question: question.trim(),
      category,
      limit,
    }),
    signal,
  })

  return payload
}
