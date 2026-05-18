# CascadeMap

**Track design system cascades. See how your design decisions propagate.**

CascadeMap analyzes your codebase to visualize how design tokens (colors, typography, spacing) cascade through components. Find inconsistent usage, track design debt, and plan systematic redesigns.

## Features

- **Design Token Tracking** — Track colors, fonts, spacing, shadows across your project
- **Cascade Visualization** — See how design decisions propagate through components
- **Inconsistency Detection** — Find hardcoded values that break consistency
- **Impact Analysis** — Know what changes when you update a design token
- **Multi-Framework** — CSS, SCSS, Tailwind, styled-components, CSS-in-JS
- **Design Debt Metrics** — Quantify design inconsistency

## Quick Start

```bash
# Scan project for design tokens
python cascade_map.py --path ~/projects/captionhook

# Generate cascade report
python cascade_map.py --path ~/projects/captionhook --report

# Find inconsistencies
python cascade_map.py --path ~/projects/captionhook --find-inconsistencies

# Output as JSON for integration
python cascade_map.py --path ~/projects/captionhook --json
```

## Output Example

```
# CascadeMap Report

## Design Tokens Found

| Token | Type | Usages | Consistency |
|-------|------|--------|-------------|
| #3B82F6 | Color | 47 | 94% |
| 1rem | Spacing | 123 | 100% |
| Inter | Font | 8 | 100% |

## Cascades

- Color `#3B82F6` used in 47 places
  → Primary buttons, links, active states
  → Risk: HIGH (47 files need review on change)

## Inconsistencies Found

- 3 similar colors: #3B82F6, #2563EB, #1D4ED8
  → Consider consolidating
- 5 different spacing values for button padding
  → 8px, 10px, 12px, 16px, 20px

## Design Debt

**Score:** 67/100 (Good)

Estimated hours to standardize: 4-6 hours
```

## Hermes Integration

```bash
# Via cron - weekly design health check
/hermes cascade-map --path ~/projects/captionhook --report
```

## Documentation

See [docs/](docs/) for full documentation.