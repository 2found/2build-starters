# Design System — __PROJECT_NAME__

The design authority for every visual or UI change. Seeded by the starter;
replace the palette and type with the product's own, but keep the rules.

## Tokens

Defined once in [app/globals.css](app/globals.css): raw values on `:root`
(overridden under `prefers-color-scheme: dark`), exposed to Tailwind through
`@theme inline`.

| Token | Utility | Use |
| --- | --- | --- |
| `--color-bg` | `bg-bg` | Page background |
| `--color-surface` | `bg-surface` | Cards, sheets, inputs |
| `--color-ink` | `text-ink` | Primary text |
| `--color-muted` | `text-muted` | Secondary text, captions |
| `--color-line` | `border-line` | Dividers and borders |
| `--color-accent` / `--color-accent-ink` | `bg-accent text-accent-ink`, `text-accent` | Primary action, links, focus |
| `--color-danger` | `text-danger` | Errors and destructive actions |
| `--radius-card` | `rounded-card` | Cards and sheets |
| `--font-sans` / `--font-mono` | `font-sans` / `font-mono` | Text / code |

## Rules

- **Reference tokens; never hardcode** a hex, rgb, radius or font family in a
  component. Need a new value? Add a token here and in `globals.css` first.
- **Reuse before building.** Check `modules/shared/ui/` (today: `Card`) for an
  existing component; extend it with a prop before adding a near-duplicate.
- Every screen works in light and dark: test both.
- Accessible by default: semantic elements (`button`, `a`, `label`), visible focus,
  text contrast ≥ 4.5:1, touch targets ≥ 44px, no information by color alone.
- Every data view designs its loading, empty and error states, not just the
  happy path.
- Layout is mobile-first and works at 360px wide without horizontal scroll.
- Copy is short and specific; error messages say what happened and what to do.

Deviating from these rules needs an explicit product decision recorded here.
