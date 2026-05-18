---
name: cascade-map
description: "Track design system cascades. Analyze how design tokens propagate through components. Find inconsistencies, track design debt, plan redesigns."
version: 1.0.0
author: powds
license: MIT
metadata:
  cascade-map:
    tags: [design-systems, css, frontend, developer-tools]
    homepage: https://github.com/powds/cascade-map
---

# CascadeMap Skill

Track design token cascades and find inconsistencies across your codebase.

## Usage

### Command Line

```bash
# Scan project
python cascade_map.py --path ~/projects/captionhook

# Generate report
python cascade_map.py --path ~/projects/captionhook --report

# Find inconsistencies
python cascade_map.py --path ~/projects/captionhook --find-inconsistencies

# JSON output
python cascade_map.py --path ~/projects/captionhook --json

# Watch mode
python cascade_map.py --path ~/projects/captionhook --watch
```

### Hermes Integration

```bash
# Weekly design health check
/hermes cascade-map --path ~/projects/captionhook --report

# Find specific token usage
/hermes cascade-map --path ~/projects/captionhook --find #3B82F6
```

## Design Token Types

| Type | Examples | Detection Pattern |
|------|----------|-------------------|
| Color | #hex, rgb(), hsl() | `/#[0-9A-Fa-f]{6}/`, `/rgb\(/` |
| Font | Inter, Roboto | `font-family:` |
| Spacing | 8px, 1rem, 0.5em | `/\d+(\.\d+)?(px|rem|em)/` |
| Shadow | box-shadow values | `box-shadow:` |
| Border | border-radius | `border-radius:` |
| Z-index | z-index values | `z-index:` |

## Cascade Analysis

CascadeMap tracks how design tokens propagate:
1. **Token** — The design value (e.g., #3B82F6)
2. **Origin** — Where it was defined (CSS variable, theme file)
3. **Usages** — All files using this token
4. **Cascade Path** — How it flows through components

## Consistency Score

| Score | Rating | Action |
|-------|--------|--------|
| 90-100 | Excellent | Maintain |
| 70-89 | Good | Minor improvements |
| 50-69 | Fair | Plan standardization |
| <50 | Poor | Major refactor needed |

## Design Debt Formula

```
design_debt = (inconsistencies_found × avg_fix_time) + (hardcoded_count × 0.5)
```

## Configuration

Create `~/.cascade-map/config.yaml`:

```yaml
analysis:
  include_patterns:
    - "*.css"
    - "*.scss"
    - "*.tsx"
    - "*.jsx"
  exclude_patterns:
    - "node_modules"
    - "*.min.css"

tokens:
  color:
    detect_hex: true
    detect_rgb: true
    detect_hsl: true
  spacing:
    detect_px: true
    detect_rem: true
    detect_em: true

thresholds:
  consistency_excellent: 90
  consistency_good: 70
  consistency_fair: 50
```

## Output Structure

```
cascade-map/
├── SKILL.md              # This file
├── cascade_map.py        # Main script
├── requirements.txt      # Dependencies
├── config.yaml           # Default config
├── docs/
│   ├── ALGORITHM.md      # How cascade analysis works
│   └── SESSION.md        # Session log
└── README.md             # Project overview
```