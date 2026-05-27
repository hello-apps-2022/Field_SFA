import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  define: {
    'process.env.NODE_ENV': JSON.stringify('production'),
    '__VUE_OPTIONS_API__': true,
    '__VUE_PROD_DEVTOOLS__': false,
  },
  build: {
    outDir: path.resolve(__dirname, '../public/sfa'),
    emptyOutDir: true,
    rollupOptions: {
      input: path.resolve(__dirname, 'index.html'),
      output: {
        entryFileNames: 'sfa.js',
        chunkFileNames: 'sfa-[hash].js',
        assetFileNames: (info) =>
          info.name?.endsWith('.css') ? 'sfa.css' : '[name]-[hash][extname]',
        inlineDynamicImports: true,
      },
    },
  },
  server: {
    port: 8080,
    proxy: {
      '/api': { target: 'http://hema.local:8000', changeOrigin: true },
      '/assets': { target: 'http://hema.local:8000', changeOrigin: true },
      '/sfa': { target: 'http://hema.local:8000', changeOrigin: true },
    },
  },
})
