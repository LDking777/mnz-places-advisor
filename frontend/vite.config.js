import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  test: {
    // URL ficticia solo para pruebas: las pruebas nunca llaman al backend real
    env: { VITE_API_BASE_URL: 'http://api.test' },
  },
})
