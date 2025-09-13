// c:\Users\Kanad\Desktop\SPARTIS_2\Spartis ApplicationExecutable\Spartis Application\vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    // This alias must match the one in your tsconfig.json
    alias: {
      '@': path.resolve(__dirname, './src/ui'),
    },
  },
  server: {
    proxy: {
      // Proxy API requests (e.g., /api/ping)
      '/api': {
        target: 'http://localhost:3001',
        changeOrigin: true,
      },
      // Proxy data file requests (e.g., /outputs/CTChest.vti)
      '/outputs': {
        target: 'http://localhost:3001',
        changeOrigin: true,
      },
    },
  },
})
