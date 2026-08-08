/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        dark: {
          950: '#04060d',
          900: '#070A11',
          800: '#0B0F19',
          700: '#111827',
          600: '#1F2937',
          500: '#374151',
        },
        arch: {
          blue: '#4F46E5',
          indigo: '#6366F1',
          emerald: '#10B981',
          amber: '#F59E0B',
          cyan: '#06B6D4',
        }
      },
      fontFamily: {
        sans: ['Inter', 'Outfit', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
