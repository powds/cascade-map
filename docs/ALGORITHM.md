# CascadeMap Algorithm

This document explains how CascadeMap tracks design token cascades.

## Overview

CascadeMap uses a four-stage pipeline:
1. **Scan** — Find all design-related files (CSS, SCSS, JSX, TSX, etc.)
2. **Extract** — Parse tokens using regex patterns
3. **Analyze** — Find similarities and build usage maps
4. **Report** — Generate consistency scores and debt estimates

## Stage 1: Scanning

### Supported File Types

```python
SUPPORTED_EXTENSIONS = {
    '.css',   # CSS
    '.scss',  # Sass
    '.sass',  # Sass
    '.less',  # Less
    '.jsx',   # React
    '.tsx',   # React TypeScript
    '.vue',   # Vue
    '.html',  # HTML
}
```

### Exclusion Patterns

```python
EXCLUDE_PATTERNS = [
    'node_modules', '.git', '__pycache__', 'dist', 'build',
    '*.min.css', '*.bundle.js', '.next', '.nuxt', '.cache'
]
```

## Stage 2: Token Extraction

### Token Patterns

```python
TOKEN_PATTERNS = {
    'color_hex': {
        'pattern': r'#[0-9A-Fa-f]{6}',
        'type': 'color',
        'weight': 2.0
    },
    'spacing_px': {
        'pattern': r'\b\d+px\b',
        'type': 'spacing',
        'weight': 1.0
    },
    # ... more patterns
}
```

### Color Normalization

```python
def normalize_hex(color: str) -> str:
    color = color.lstrip('#').lower()
    if len(color) == 3:
        color = color[0]*2 + color[1]*2 + color[2]*2
    return '#' + color
```

## Stage 3: Similarity Analysis

### Color Similarity (RGB Euclidean Distance)

```python
def color_similarity(c1: str, c2: str) -> float:
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)

    distance = ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5
    max_distance = (255 ** 2 * 3) ** 0.5

    return 1 - (distance / max_distance)
```

- Threshold: 85% similarity → considered "similar"
- Groups of 2+ similar colors flagged for consolidation

### Spacing Similarity (Pixel Tolerance)

```python
def spacing_normalize(spacing: str) -> float:
    if 'px' in spacing: return float(spacing.replace('px', ''))
    if 'rem' in spacing: return float(spacing.replace('rem', '')) * 16
    if 'em' in spacing: return float(spacing.replace('em', '')) * 16
    return float(spacing)
```

- Tolerance: within 2px considered "similar"
- Groups of 2+ similar values flagged

## Stage 4: Scoring

### Consistency Score Formula

```
score = 100 - (similar_color_groups × 5) - (similar_spacing_groups × 2)

clamped to [0, 100]
```

| Score | Rating | Action |
|-------|--------|--------|
| 90-100 | Excellent | Maintain |
| 70-89 | Good | Minor improvements |
| 50-69 | Fair | Plan standardization |
| <50 | Poor | Major refactor needed |

### Design Debt Estimation

```python
color_debt = similar_color_groups × 0.5  # hours per group
spacing_debt = similar_spacing_groups × 0.25  # hours per group
file_review = total_files × 0.05  # hours per file
total_hours = color_debt + spacing_debt + file_review
estimated_cost = total_hours × hourly_rate  # $50/hr default
```

## Token Types Supported

| Type | Detection | Weight |
|------|-----------|--------|
| Color (hex) | `#RGB` or `#RRGGBB` | 2.0 |
| Color (rgb/rgba/hsl) | `rgb()`, `rgba()`, `hsl()` | 1.5 |
| Spacing (px) | `NNpx` | 1.0 |
| Spacing (rem/em) | `NNrem`, `NNem` | 1.0 |
| Font family | `font-family:` | 1.5 |
| Font size | `font-size:` | 1.0 |
| Border radius | `border-radius:` | 0.8 |
| Box shadow | `box-shadow:` | 0.8 |
| Z-index | `z-index:` | 0.5 |

## Limitations

CascadeMap uses regex, not CSS parsers:
- Cannot detect CSS custom properties (variables) reliably
- Cannot understand semantic meaning of colors
- Cannot track design intent
- Cannot parse complex CSS functions

Best for: finding inconsistencies in raw values
Not for: semantic design analysis, design system compliance

## Future Enhancements

1. **CSS Variable Tracking** — `--primary-color` instead of `#hex`
2. **Tailwind Class Detection** — `class="bg-blue-500"`
3. **Design Token Files** — `design-tokens.json` import
4. **Cascade Visualization** — D3.js diagram of token propagation
5. **Framework Integration** — Chakra, Material UI, Ant Design token mapping