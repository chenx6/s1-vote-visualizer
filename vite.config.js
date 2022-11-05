import { defineConfig } from "vite"

export default defineConfig({
    base: "/s1-vote-visualizer/",
    build: {
        outDir: "./docs"
    },
    server: {
        open: '/index.html'
    }
})