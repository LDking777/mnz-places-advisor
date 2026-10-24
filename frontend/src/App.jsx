import { useState } from 'react'
import { DEFAULT_CATEGORY } from './constants/categories'
import { usePlaces } from './hooks/usePlaces'
import { useChat } from './hooks/useChat'
import HeroSection from './components/HeroSection'
import PlacesGrid from './components/PlacesGrid'
import ChatPanel from './components/ChatPanel'
import Footer from './components/Footer'

/**
 * Componente raíz — composición pura.
 * El estado de categoría vive aquí y se propaga a hijos y hooks.
 */
function App() {
  const [category, setCategory] = useState(DEFAULT_CATEGORY)
  const { data, status, error } = usePlaces(category)
  const chat = useChat(category)

  return (
    <>
      <main className="mx-auto w-full max-w-5xl px-4 py-10 sm:px-6 lg:px-8">
        <HeroSection category={category} onCategoryChange={setCategory} />
        <PlacesGrid data={data} status={status} error={error} />
        <ChatPanel {...chat} />
      </main>
      <Footer />
    </>
  )
}

export default App
