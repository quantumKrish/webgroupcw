import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
    base:
        mode == "development"
            ? "http://localhost:5173/"
            : "/static/api/spa/",
    build: {
        emptyOutDir: true,
        outDir: "../api/static/api/spa",
    },
    plugins: [vue()],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src'),
        },
    },
    server: {
        proxy: {
            '/api': {
                target: 'http://localhost:8000',
                changeOrigin: true,
            },
            '/login': {
                target: 'http://localhost:8000',
                changeOrigin: true,
            },
            '/logout': {
                target: 'http://localhost:8000',
                changeOrigin: true,
            },
            '/signup': {
                target: 'http://localhost:8000',
                changeOrigin: true,
            },
        },
    },
}));