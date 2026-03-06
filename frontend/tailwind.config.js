/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts}'],
  theme: {
    extend: {
      colors: {
        primary: { 50:'#eff6ff', 100:'#dbeafe', 500:'#3b82f6', 600:'#2563eb', 700:'#1d4ed8' },
        brand: { DEFAULT: '#2563eb', dark: '#1d4ed8', light: '#3b82f6' },
      },
    },
  },
  plugins: [],
}
