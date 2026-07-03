import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";
import { fileURLToPath } from "node:url";

const dirname = path.dirname(fileURLToPath(import.meta.url));

const devProxyTarget = process.env.VITE_DEV_PROXY_TARGET || "http://127.0.0.1:18080";

export default defineConfig({
  plugins: [react()],
  base: "/",
  envPrefix: ["VITE_", "ENABLE_"],
  server: {
    proxy: {
      "/api/v1": {
        target: devProxyTarget,
        changeOrigin: true,
        secure: false
      }
    }
  },
  resolve: {
    alias: {
      "@": path.resolve(dirname, "src")
    }
  },
  build: {
    outDir: "dist",
    assetsDir: "_assets",
    emptyOutDir: true
  }
});
