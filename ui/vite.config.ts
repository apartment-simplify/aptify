import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": "/src"
    }
  },
  server: {
    port: 3000,
    strictPort: true,
    open: true
  },
  preview: {
    port: 4173
  }
});
