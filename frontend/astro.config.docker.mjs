// @ts-check
import { defineConfig } from "astro/config";
import tailwind from "@astrojs/tailwind";
import react from "@astrojs/react";
import node from "@astrojs/node";

// Docker/self-hosted config — uses Node adapter instead of Vercel
export default defineConfig({
  output: "server",
  adapter: node({ mode: "standalone" }),
  integrations: [
    tailwind(),
    react(),
  ],
  vite: {
    cacheDir: 'node_modules/.cache/.vite',
    optimizeDeps: {
      include: [
        'react',
        'react-dom',
        'zustand',
        'framer-motion',
        'date-fns',
        'clsx',
        'class-variance-authority',
        'tailwind-merge',
        'zod',
      ],
    },
  },
  devToolbar: {
    enabled: false,
  },
  server: {
    host: true,
  },
});
