import { useEffect, useReducer } from 'react'
import { fetchRecommendations } from '../services/api'

const initialState = { data: null, status: 'loading', error: '' }

function reducer(state, action) {
  switch (action.type) {
    case 'FETCH_INIT':
      return { ...state, status: 'loading', error: '' }
    case 'FETCH_SUCCESS':
      return { data: action.payload, status: 'success', error: '' }
    case 'FETCH_ERROR':
      return { ...state, status: 'error', error: action.message }
    default:
      return state
  }
}

/**
 * Hook que encapsula la obtención de recomendaciones turísticas.
 *
 * @param {string} category — categoría Geoapify activa.
 * @returns {{ data, status, error }}
 *   - data:   payload del backend (null mientras carga)
 *   - status: 'loading' | 'success' | 'error'
 *   - error:  mensaje de error (cadena vacía si no hay error)
 */
export function usePlaces(category) {
  const [state, dispatch] = useReducer(reducer, initialState)

  useEffect(() => {
    const controller = new AbortController()
    dispatch({ type: 'FETCH_INIT' })

    fetchRecommendations({ category, signal: controller.signal })
      .then((payload) => {
        dispatch({ type: 'FETCH_SUCCESS', payload })
      })
      .catch((err) => {
        if (controller.signal.aborted) return
        dispatch({ type: 'FETCH_ERROR', message: err.message })
      })

    return () => controller.abort()
  }, [category])

  return state
}
