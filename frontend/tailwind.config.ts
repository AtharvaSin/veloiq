import type { Config } from 'tailwindcss'

const config: Config = {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // DESIGN.md obsidian palette
        obsidian: '#0d0d14',
        surface: '#12121e',
        elevated: '#1a1a2e',
        void: '#0a0a0a',
        divider: '#1f1f35',
        // Accent palette
        accent: {
          DEFAULT: '#00D492',
          hover: '#00b87d',
        },
        warn: '#E8B931',
        danger: '#FF6B6B',
        // Text palette
        primary: '#EEEAE4',
        secondary: '#A09D95',
        muted: '#606060',
        // Block identity (3px borders only, never fills)
        block: {
          cert: '#0EA5E9',
          tcc: '#8B5CF6',
          sales: '#22C55E',
        },
      },
      fontFamily: {
        sans: ['"DM Sans"', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"JetBrains Mono"', '"Fira Code"', 'monospace'],
      },
      borderRadius: {
        tight: '4px',
        DEFAULT: '8px',
        modal: '12px',
      },
      fontSize: {
        // Label pattern from DESIGN.md
        'label': ['0.75rem', { letterSpacing: '0.15em', fontWeight: '600' }],
      },
      letterSpacing: {
        label: '0.15em',
      },
    },
  },
  plugins: [],
}

export default config

