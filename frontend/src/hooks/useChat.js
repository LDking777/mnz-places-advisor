import { useState } from 'react'
import { askAssistant } from '../services/api'

/**
 * Hook que encapsula la interacción con el asistente turístico IA.
 *
 * @returns {{ question, setQuestion, response, loading, error, submit }}
 */
export function useChat(category) {
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [response, setResponse] = useState(null)

  async function submit(event) {
    event.preventDefault()
    const trimmed = question.trim()
    if (!trimmed || loading) return

    setLoading(true)
    setError('')
    setResponse(null)

    try {
      const payload = await askAssistant({
        question: trimmed,
        category,
        limit: 12,
      })
      setResponse(payload)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return { question, setQuestion, response, loading, error, submit }
}
