export default {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
    './node_modules/frappe-ui/src/**/*.{vue,js,ts}',
  ],
  theme: {
    extend: {
      colors: {
        // Frappe design tokens as plain tailwind colors
        'ink-gray-9': '#1f272e',
        'ink-gray-8': '#2e3c48',
        'ink-gray-7': '#4c5960',
        'ink-gray-6': '#687178',
        'ink-gray-5': '#8d979e',
        'ink-gray-4': '#a6aeb3',
        'ink-gray-3': '#c0c6ca',
        'surface-gray-1': '#f9fafb',
        'surface-gray-2': '#f4f5f6',
        'surface-gray-3': '#ebedf0',
        'outline-gray-1': '#f0f1f3',
        'outline-gray-2': '#e2e6e9',
        'outline-gray-3': '#d0d5d8',
      },
    },
  },
  plugins: [],
}
