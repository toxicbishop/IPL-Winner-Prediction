/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx,js,jsx}'],
  darkMode: ['selector', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        ink: 'var(--color-bg)',
        'ink-deep': 'var(--color-bg-deep)',
        surface: {
          DEFAULT: 'var(--color-surface)',
          alt: 'var(--color-surface-alt)',
          container: 'var(--color-surface-container)',
          high: 'var(--color-surface-high)',
          highest: 'var(--color-surface-highest)',
        },
        hair: {
          DEFAULT: 'var(--color-border)',
          hover: 'var(--color-border-hover)',
          strong: 'var(--color-border-strong)',
        },
        saffron: {
          DEFAULT: 'var(--color-primary)',
          dim: 'var(--color-primary-dim)',
          fixed: 'var(--color-primary-fixed)',
          muted: 'var(--color-primary-muted)',
          on: 'var(--color-on-primary)',
        },
        grass: {
          DEFAULT: 'var(--color-secondary)',
          container: 'var(--color-secondary-container)',
          on: 'var(--color-on-secondary)',
        },
        crimson: {
          DEFAULT: 'var(--color-tertiary)',
          dim: 'var(--color-tertiary-dim)',
          container: 'var(--color-tertiary-container)',
        },
        paper: {
          DEFAULT: 'var(--color-text-main)',
          muted: 'var(--color-text-muted)',
          soft: 'var(--color-text-secondary)',
          faint: 'var(--color-text-faint)',
        },
      },
      fontFamily: {
        display: ['Fraunces', 'Iowan Old Style', 'Georgia', 'serif'],
        sans: ['Archivo', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['"IBM Plex Mono"', '"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      letterSpacing: {
        footnote: '0.22em',
        mono: '0.14em',
      },
      borderRadius: {
        none: '0',
      },
      transitionTimingFunction: {
        pavilion: 'cubic-bezier(0.2, 0.6, 0.2, 1)',
      },
      boxShadow: {
        none: 'none',
      },
      animation: {
        'rise-in': 'riseIn 0.5s cubic-bezier(0.2, 0.6, 0.2, 1) forwards',
        'fade-in': 'fadeIn 0.35s cubic-bezier(0.2, 0.6, 0.2, 1) forwards',
      },
    },
  },
  plugins: [],
  corePlugins: {
    // Keep border-radius utilities but default them all to 0 via our tokens
    preflight: true,
  },
};
