/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        tally: {
          // Verde moderno (principal)
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22C55E', // Principal
          600: '#16A34A', // Más profundo
          700: '#15803d',
          800: '#166534',
          900: '#145231',
          
          // Grises neutrales
          text: '#1F2937',
          light: '#F9FAFB',
          border: '#E5E7EB',
          hover: '#F3F4F6',
          
          // Acento
          accent: '#38BDF8',
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        display: ['Sohne', 'Inter', 'sans-serif'],
      },
      spacing: {
        '4.5': '1.125rem',
        '7.5': '1.875rem',
      },
      borderRadius: {
        'xl': '0.75rem',
        '2xl': '1rem',
      },
      boxShadow: {
        'sm-tally': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'md-tally': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        'lg-tally': '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
      },
      transitionDuration: {
        '200': '200ms',
        '300': '300ms',
      },
    },
  },
  plugins: [],
}
