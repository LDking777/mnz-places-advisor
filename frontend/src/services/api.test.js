import { afterEach, describe, expect, it, vi } from 'vitest'
import { askAssistant, fetchRecommendations } from './api.js'

function mockFetch(body, { ok = true, status = 200 } = {}) {
  const fetchMock = vi.fn().mockResolvedValue({
    ok,
    status,
    json: () => Promise.resolve(body),
  })
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('fetchRecommendations', () => {
  it('llama al endpoint correcto con la categoría', async () => {
    const fetchMock = mockFetch({ city: 'Manizales', count: 0, places: [] })

    const data = await fetchRecommendations({ category: 'natural' })

    const calledUrl = fetchMock.mock.calls[0][0]
    expect(calledUrl.toString()).toBe(
      'http://api.test/api/v1/places/recommendations?category=natural',
    )
    expect(data.city).toBe('Manizales')
  })

  it('falla si el backend devuelve una estructura inesperada', async () => {
    mockFetch({ city: 'Manizales' })
    await expect(fetchRecommendations()).rejects.toThrow('estructura de datos inesperada')
  })

  it('propaga el mensaje de error del backend', async () => {
    mockFetch({ error: { message: 'Proveedor no disponible' } }, { ok: false, status: 502 })
    await expect(fetchRecommendations()).rejects.toThrow('Proveedor no disponible')
  })
})

describe('askAssistant', () => {
  it('envía la pregunta por POST como JSON', async () => {
    const fetchMock = mockFetch({ answer: 'ok' })

    await askAssistant({ question: '  ¿Dónde almorzar?  ', category: 'catering.restaurant' })

    const [url, options] = fetchMock.mock.calls[0]
    expect(url.toString()).toBe('http://api.test/api/v1/chat/assistant')
    expect(options.method).toBe('POST')
    expect(JSON.parse(options.body)).toEqual({
      question: '¿Dónde almorzar?',
      category: 'catering.restaurant',
      limit: 12,
    })
  })
})
