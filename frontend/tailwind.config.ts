import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: ['class'],
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // shadcn semantic colors (backed by CSS variables in index.css)
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
        // DESIGN.md obsidian palette (direct hex, used for custom components)
        obsidian: '#0d0d14',
        surface: '#12121e',
        elevated: '#1a1a2e',
        void: '#0a0a0a',
        divider: '#1f1f35',
        accent: {
          DEFAULT: '#00D492',
          hover: '#00b87d',
          foreground: '#0d0d14',
        },
        warn: '#E8B931',
        danger: '#FF6B6B',
        primary: {
          DEFAULT: '#EEEAE4',
          foreground: '#0d0d14',
        },
        secondary: {
          DEFAULT: '#A09D95',
          foreground: '#0d0d14',
        },
        muted: {
          DEFAULT: '#606060',
          foreground: '#A09D95',
        },
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
        DEFAULT: 'var(--radius)',
        modal: '12px',
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      fontSize: {
        // Label pattern from DESIGN.md
        'label': ['0.75rem', { letterSpacing: '0.15em', fontWeight: '600' }],
      },
      letterSpacing: {
        label: '0.15em',
      },
      keyframes: {
        'accordion-down': {
          from: { height: '0' },
          to: { height: 'var(--radix-accordion-content-height)' },
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: '0' },
        },
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
}

export default config

