import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: '../server/static',
    emptyOutDir: true,
  },
  server: {
    proxy: {
      '/convert': 'http://localhost:5000',
      '/formats': 'http://localhost:5000',
    }
  }
})
