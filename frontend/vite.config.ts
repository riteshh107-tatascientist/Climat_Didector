/// <reference types="node" />
import { defineConfig, loadEnv, type ConfigEnv } from "vite";
import react from "@vitejs/plugin-react";

// Using Vite's loadEnv (the documented pattern for reading env vars inside
// vite.config.ts) instead of relying on ambient `process.env` alone.
// `process` itself is still Node's global, typed via the `@types/node`
// devDependency + tsconfig.node.json's `"types": ["node"]` — both are
// required for `tsc -b` to type-check this file cleanly (see
// TS2580 "Cannot find name 'process'" if either is missing).
export default defineConfig(({ mode }: ConfigEnv) => {
  const env = loadEnv(mode, process.cwd(), "");

  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: {
        "/api": {
          target: env.VITE_API_PROXY_TARGET || "http://localhost:8000",
          changeOrigin: true,
        },
      },
    },
    build: {
      outDir: "dist",
      sourcemap: false,
    },
  };
});
