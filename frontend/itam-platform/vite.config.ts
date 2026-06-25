import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";

export default defineConfig({
  plugins: [react()],
  base: "/",
  envPrefix: ["VITE_", "ENABLE_"],
  server: {
    proxy: {
      "/api/v1": {
        target: "http://[::1]:8080",
        changeOrigin: true,
        secure: false
      }
    }
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src")
    }
  },
  build: {
    outDir: "dist",
    assetsDir: "_assets",
    emptyOutDir: true
  }
});
