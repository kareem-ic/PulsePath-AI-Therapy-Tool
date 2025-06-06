import type { Config } from 'tailwindcss'

export default {
  content: [
    './index.html',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: '#5b6dfa',
          dark:    '#3844b2',
        },
      },
    },
  },
  plugins: [],
} satisfies Config
