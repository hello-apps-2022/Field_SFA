import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import frappeUIPlugin from 'frappe-ui/vite'

export default defineConfig({
  plugins: [
    frappeUIPlugin({
      frappeProxy: true,
      jinjaBootData: true,
      buildConfig: {
        indexHtmlPath: '../sfa_core/www/sfa.html',
        emptyOutDir: true,
        sourcemap: false,
      },
    }),
    vue(),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  server: {
    fs: {
      allow: [path.resolve(__dirname, '..')],
    },
  },
  optimizeDeps: {
    include: ['feather-icons'],
  },
})
