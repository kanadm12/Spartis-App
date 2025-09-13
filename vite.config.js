import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, 'src/ui'),
        },
    },
    base: './',
    build: {
        outDir: 'dist-electron/react',
    },
    server: {
        port: 5123,
        strictPort: true,
    },
});
