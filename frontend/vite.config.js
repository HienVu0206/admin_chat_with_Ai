import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path' // Thêm dòng này

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'), // Cấu hình để @ trỏ về src
    },
  },
})