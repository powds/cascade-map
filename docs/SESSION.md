# CascadeMap Session Log

## Session: 2026-05-18

### What was built
- **CascadeMap** — design system cascade tracker
- Tracks design tokens (colors, spacing, fonts) across codebase
- Finds similar values that should be consolidated
- Calculates design consistency score
- Estimates design debt in hours

### Project location
`~/projects/cascade-map/`

### GitHub
https://github.com/powds/cascade-map

### Test results (captionhook)
- Files Scanned: 14
- Consistency Score: 83.0/100 (Good)
- Unique Colors: 45
- Unique Spacing Values: 39
- Total Token Usages: 319
- Similar Colors: 1 group (#3344dd, #2222dd)
- Similar Spacing: 6 groups
- Design Debt: 2.7 hours ($135)

### Files created
```
cascade-map/
├── SKILL.md           # Hermes skill integration
├── cascade_map.py     # Main analysis script (21KB)
├── config.yaml        # Configuration
├── requirements.txt   # Dependencies
├── README.md          # Project docs
└── docs/
    ├── ALGORITHM.md   # How cascade analysis works (to be created)
    └── SESSION.md     # This file
```

### How it works
1. Scan files for CSS-like patterns (colors, spacing, fonts, etc.)
2. Build token usage map with file references
3. Find similar values (colors within 85% similarity, spacing within 2px)
4. Calculate consistency score (100 - penalties)
5. Estimate design debt based on consolidation work

### Consistency score formula
- Base: 100
- Each similar color group: -5 points
- Each similar spacing group: -2 points
- Clamped to 0-100

### Coverage ratings
| Score | Rating | Action |
|-------|--------|--------|
| 90-100 | Excellent | Maintain |
| 70-89 | Good | Minor improvements |
| 50-69 | Fair | Plan standardization |
| <50 | Poor | Major refactor needed |

### Next steps
1. Add CSS variable tracking (--primary-color)
2. Add framework-specific detection (Tailwind classes)
3. Support design token files (design-tokens.json)
4. Add cascade path visualization
5. CI integration for design debt tracking

### Key decisions
- Regex-based token detection (fast, no AST needed)
- Color similarity via RGB Euclidean distance
- Spacing normalization to pixels for comparison
- Design debt estimated at $50/hour