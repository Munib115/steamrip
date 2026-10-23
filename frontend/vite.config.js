import { defineConfig } from "vite";

export default defineConfig({
  root: ".",
  server: {
    port: 5173,
    proxy: {
      "/api": "http://localhost:8000",
      "/download": "http://localhost:8000",
      "/games": "http://localhost:8000",
      "/health": "http://localhost:8000",
      "/posters": "http://localhost:8000",
    },
  },
  build: {
    outDir: "dist",
  },
});