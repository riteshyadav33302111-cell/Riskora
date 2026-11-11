/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          50:  '#e8eaf6',
          100: '#c5c8e8',
          200: '#9fa3d8',
          300: '#777ec8',
          400: '#5861bd',
          500: '#3845b2',
          600: '#2a3a9e',
          700: '#1a2d87',
          800: '#0d2070',
          900: '#060f52',
          950: '#030927',
        },
        cyber: {
          purple: '#8b5cf6',
          cyan:   '#06b6d4',
          pink:   '#ec4899',
          green:  '#10b981',
          red:    '#ef4444',
          orange: '#f59e0b',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow':  'spin 3s linear infinite',
        'fade-in':    'fadeIn 0.5s ease-in-out',
        'slide-up':   'slideUp 0.4s ease-out',
        'glow':       'glow 2s ease-in-out infinite alternate',
        'scan-line':  'scanLine 2s linear infinite',
      },
      keyframes: {
        fadeIn: {
          '0%':   { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%':   { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        glow: {
          '0%':   { boxShadow: '0 0 5px #8b5cf6, 0 0 10px #8b5cf6' },
          '100%': { boxShadow: '0 0 20px #8b5cf6, 0 0 40px #06b6d4' },
        },
        scanLine: {
          '0%':   { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(400%)' },
        },
      },
      backgroundImage: {
        'grid-pattern': `
          linear-gradient(rgba(139, 92, 246, 0.05) 1px, transparent 1px),
          linear-gradient(90deg, rgba(139, 92, 246, 0.05) 1px, transparent 1px)
        `,
        'cyber-gradient': 'linear-gradient(135deg, #060f52 0%, #0d2070 50%, #030927 100%)',
        'card-gradient':  'linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%)',
      },
      backgroundSize: {
        'grid': '30px 30px',
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
