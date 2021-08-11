import graphql from "@rollup/plugin-graphql";
import { svelte } from "@sveltejs/vite-plugin-svelte";
import { defineConfig } from "vite";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [svelte(), graphql()],
  build: {
    lib: {
      entry: "src/main.ts",
      name: "simpl",
    },
    outDir: "../simpl/static/simpl",
    emptyOutDir: true,
  },
});
