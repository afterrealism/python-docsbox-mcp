import { defineConfig, presetUno, presetTypography, presetIcons } from 'unocss';

export default defineConfig({
  presets: [
    presetUno(),
    presetTypography({
      cssExtend: {
        'pre,code': { 'font-family': 'var(--font-mono)' },
        'pre': {
          background: 'var(--code-bg)',
          border: '1px solid var(--border)',
          'border-radius': '6px',
          padding: '0.85rem 1rem',
          'font-size': '0.9rem',
          'line-height': '1.55'
        },
        'code': {
          background: 'var(--code-bg)',
          padding: '0.12rem 0.35rem',
          'border-radius': '4px',
          'font-size': '0.92em'
        },
        'pre code': { background: 'transparent', padding: 0 },
        'h2': { 'scroll-margin-top': '5rem' },
        'h3': { 'scroll-margin-top': '5rem' },
        'a': { color: 'var(--accent)', 'text-decoration': 'none' },
        'a:hover': { 'text-decoration': 'underline' }
      }
    }),
    presetIcons()
  ],
  theme: {
    fontFamily: {
      sans: 'var(--font-sans)',
      mono: 'var(--font-mono)'
    }
  }
});
