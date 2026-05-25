import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      'vue': 'vue/dist/vue.esm-bundler.js'
    }
  },
  build: {
    outDir: 'public/dist',
    emptyOutDir: true,
    lib: {
      entry: path.resolve(__dirname, 'src/main.js'),
      name: 'SFA_Core',
      fileName: () => 'sfa_desk.bundle.js',
      formats: ['iife']
    },
    rollupOptions: {
      external: ['frappe'],
      output: {
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name.split('.')
          const ext = info[info.length - 1]
          if (ext === 'css') {
            return 'sfa_core.bundle.css'
          }
          return '[name][extname]'
        },
        globals: {
          frappe: 'frappe'
        }
      }
    }
  }
})
