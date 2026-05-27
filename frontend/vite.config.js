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
    'process.env': '{}',
    'process.env.NODE_ENV': JSON.stringify('production'),
    
  },
  build: {
    outDir: path.resolve(__dirname, '../public/dist'),
    emptyOutDir: true,
    lib: {
      entry: path.resolve(__dirname, 'src/main.js'),
      name: 'SFA',
      fileName: () => 'sfa_desk.bundle.js',
      formats: ['iife'],
    },
    rollupOptions: {
      external: [],
      output: {
        assetFileNames: (info) =>
          info.name?.endsWith('.css') ? 'sfa_core.bundle.css' : '[name][extname]',
        globals: {},
        inlineDynamicImports: true,
      },
    },
  },
  server: {
    proxy: {
      '/api': { target: 'http://hema.local:8000', changeOrigin: true },
      '/assets': { target: 'http://hema.local:8000', changeOrigin: true },
    },
  },
})
