// @ts-check
import { defineConfig } from "astro/config";
import tailwind from "@astrojs/tailwind";
import react from "@astrojs/react";
import vercel from "@astrojs/vercel";
import node from "@astrojs/node";

const isVercel = process.env.VERCEL === "1";

// https://astro.build/config
export default defineConfig({
  output: isVercel ? "static" : "server",
  adapter: isVercel ? vercel() : node({ mode: "standalone" }),
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
