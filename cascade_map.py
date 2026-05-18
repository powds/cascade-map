#!/usr/bin/env python3
"""
CascadeMap - Design System Cascade Tracker

Analyzes codebase to track design token cascades,
find inconsistencies, and quantify design debt.
"""

import argparse
import os
import re
import sys
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# === TOKEN PATTERNS ===

TOKEN_PATTERNS = {
    'color_hex': {
        'pattern': r'#[0-9A-Fa-f]{6}',
        'type': 'color',
        'weight': 2.0
    },
    'color_hex3': {
        'pattern': r'#[0-9A-Fa-f]{3}',
        'type': 'color',
        'weight': 2.0
    },
    'color_rgb': {
        'pattern': r'rgb\s*\([^)]+\)',
        'type': 'color',
        'weight': 1.5
    },
    'color_rgba': {
        'pattern': r'rgba\s*\([^)]+\)',
        'type': 'color',
        'weight': 1.5
    },
    'color_hsl': {
        'pattern': r'hsl\s*\([^)]+\)',
        'type': 'color',
        'weight': 1.5
    },
    'spacing_px': {
        'pattern': r'\b\d+px\b',
        'type': 'spacing',
        'weight': 1.0
    },
    'spacing_rem': {
        'pattern': r'\b\d+(\.\d+)?rem\b',
        'type': 'spacing',
        'weight': 1.0
    },
    'spacing_em': {
        'pattern': r'\b\d+(\.\d+)?em\b',
        'type': 'spacing',
        'weight': 1.0
    },
    'font_family': {
        'pattern': r'font-family\s*:\s*[^;]+',
        'type': 'font',
        'weight': 1.5
    },
    'font_size': {
        'pattern': r'font-size\s*:\s*[^;]+',
        'type': 'font-size',
        'weight': 1.0
    },
    'border_radius': {
        'pattern': r'border-radius\s*:\s*[^;]+',
        'type': 'border-radius',
        'weight': 0.8
    },
    'box_shadow': {
        'pattern': r'box-shadow\s*:\s*[^;]+',
        'type': 'shadow',
        'weight': 0.8
    },
    'z_index': {
        'pattern': r'z-index\s*:\s*[^;]+',
        'type': 'z-index',
        'weight': 0.5
    },
}

EXCLUDE_PATTERNS = [
    'node_modules', '.git', '__pycache__', 'dist', 'build',
    '*.min.css', '*.bundle.js', '.next', '.nuxt', '.cache'
]

# === SIMILARITY DETECTION ===

def color_similarity(c1: str, c2: str) -> float:
    """Calculate similarity between two hex colors (0-1)."""
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = hex_color[0]*2 + hex_color[1]*2 + hex_color[2]*2
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    try:
        r1, g1, b1 = hex_to_rgb(c1)
        r2, g2, b2 = hex_to_rgb(c2)

        # Euclidean distance in RGB space
        distance = ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5
        max_distance = (255 ** 2 * 3) ** 0.5  # Max possible distance

        return 1 - (distance / max_distance)
    except:
        return 0.0

def normalize_hex(color: str) -> str:
    """Normalize hex color to 6-digit lowercase."""
    color = color.lstrip('#').lower()
    if len(color) == 3:
        color = color[0]*2 + color[1]*2 + color[2]*2
    return '#' + color

def spacing_normalize(spacing: str) -> float:
    """Normalize spacing to pixels."""
    spacing = spacing.strip()
    if 'px' in spacing:
        return float(spacing.replace('px', ''))
    elif 'rem' in spacing:
        return float(spacing.replace('rem', '')) * 16
    elif 'em' in spacing:
        return float(spacing.replace('em', '')) * 16
    return float(spacing)

# === FILE ANALYSIS ===

def should_exclude(path: str) -> bool:
    """Check if path should be excluded."""
    path_lower = path.lower()
    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith('*'):
            if path_lower.endswith(pattern[1:].lower()):
                return True
        elif pattern in path_lower:
            return True
    return False

def get_supported_extensions() -> Set[str]:
    """Get all supported file extensions."""
    return {'.css', '.scss', '.sass', '.less', '.jsx', '.tsx', '.vue', '.html'}

def extract_tokens(content: str) -> Dict[str, List[Dict]]:
    """Extract design tokens from content."""
    tokens = defaultdict(list)

    for token_name, token_info in TOKEN_PATTERNS.items():
        pattern = token_info['pattern']
        token_type = token_info['type']

        for match in re.finditer(pattern, content):
            value = match.group(0)
            line_num = content[:match.start()].count('\n') + 1

            # Normalize color values
            if token_type == 'color':
                if value.startswith('#'):
                    value = normalize_hex(value)
                elif 'rgb' in value or 'hsl' in value:
                    value = value.lower().replace(' ', '')

            tokens[token_type].append({
                'value': value,
                'token_name': token_name,
                'line': line_num,
                'raw': match.group(0)
            })

    return dict(tokens)

def analyze_file(file_path: str) -> Dict:
    """Analyze a single file for design tokens."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        tokens = extract_tokens(content)

        return {
            'path': file_path,
            'tokens': tokens,
            'total_tokens': sum(len(v) for v in tokens.values()),
            'language': detect_language(file_path)
        }
    except Exception as e:
        return {'error': str(e), 'path': file_path}

def detect_language(file_path: str) -> str:
    """Detect language/framework from extension."""
    ext = os.path.splitext(file_path)[1].lower()
    lang_map = {
        '.css': 'css',
        '.scss': 'scss',
        '.sass': 'sass',
        '.less': 'less',
        '.jsx': 'jsx',
        '.tsx': 'tsx',
        '.vue': 'vue',
        '.html': 'html',
    }
    return lang_map.get(ext, 'unknown')

# === PROJECT ANALYSIS ===

def analyze_project(root_path: str) -> Dict:
    """Analyze entire project for design tokens."""
    root_path = os.path.expanduser(root_path)
    if not os.path.exists(root_path):
        return {'error': f'Path not found: {root_path}'}

    supported_ext = get_supported_extensions()
    files = []

    for ext in supported_ext:
        for file_path in Path(root_path).rglob(f'*{ext}'):
            if not should_exclude(str(file_path)):
                files.append(str(file_path))

    results = []
    all_tokens = defaultdict(list)

    for file_path in files:
        result = analyze_file(file_path)
        if 'error' not in result:
            results.append(result)
            # Merge tokens
            for token_type, token_list in result['tokens'].items():
                all_tokens[token_type].extend(token_list)

    return {
        'project': os.path.basename(root_path),
        'path': root_path,
        'files': results,
        'total_files': len(results),
        'all_tokens': dict(all_tokens),
        'analyzed_at': datetime.now().isoformat()
    }

# === CASCADE ANALYSIS ===

def build_token_usage_map(all_tokens: Dict) -> Dict[str, Dict]:
    """Build map of each unique token and its usage count."""
    token_map = defaultdict(lambda: {
        'values': [],
        'files': set(),
        'count': 0,
        'type': None
    })

    for token_type, token_list in all_tokens.items():
        for token in token_list:
            value = token['value']
            file_path = token.get('path', 'unknown')

            token_map[value]['values'].append(token)
            token_map[value]['files'].add(file_path)
            token_map[value]['count'] += 1
            token_map[value]['type'] = token_type

    # Convert sets to counts
    result = {}
    for value, data in token_map.items():
        result[value] = {
            'type': data['type'],
            'count': data['count'],
            'file_count': len(data['files']),
            'files': list(data['files'])[:10]  # Limit to 10 files
        }

    return result

def find_similar_colors(token_usage: Dict, threshold: float = 0.85) -> List[Dict]:
    """Find similar colors that might need consolidation."""
    colors = {k: v for k, v in token_usage.items() if v['type'] == 'color'}

    similar_groups = []
    processed = set()

    for color1, data1 in colors.items():
        if color1 in processed:
            continue

        group = [color1]
        for color2, data2 in colors.items():
            if color1 == color2 or color2 in processed:
                continue

            similarity = color_similarity(color1, color2)
            if similarity >= threshold:
                group.append(color2)
                processed.add(color2)

        if len(group) > 1:
            similar_groups.append(group)
            for c in group:
                processed.add(c)

    return similar_groups

def find_similar_spacing(token_usage: Dict, tolerance: float = 2.0) -> List[Dict]:
    """Find similar spacing values that might need consolidation."""
    spacing = {k: v for k, v in token_usage.items() if v['type'] == 'spacing'}

    similar_groups = []
    processed = set()

    for sp1, data1 in spacing.items():
        if sp1 in processed:
            continue

        group = [sp1]
        val1 = spacing_normalize(sp1)

        for sp2, data2 in spacing.items():
            if sp1 == sp2 or sp2 in processed:
                continue

            val2 = spacing_normalize(sp2)
            if abs(val1 - val2) <= tolerance:
                group.append(sp2)
                processed.add(sp2)

        if len(group) > 1:
            similar_groups.append(group)
            for s in group:
                processed.add(s)

    return similar_groups

def calculate_consistency_score(token_usage: Dict, similar_colors: List, similar_spacing: List) -> Tuple[float, str]:
    """Calculate overall design consistency score (0-100)."""
    if not token_usage:
        return 100.0, "Excellent"

    total_items = len(token_usage)

    # Penalty for similar items (colors within 85% similarity)
    color_penalty = len(similar_colors) * 5

    # Penalty for inconsistent spacing
    spacing_penalty = len(similar_spacing) * 2

    # Base score
    score = 100.0 - (color_penalty + spacing_penalty)

    # Clamp
    score = max(0.0, min(100.0, score))

    # Rating
    if score >= 90:
        rating = "Excellent"
    elif score >= 70:
        rating = "Good"
    elif score >= 50:
        rating = "Fair"
    else:
        rating = "Poor"

    return round(score, 1), rating

def estimate_design_debt(similar_colors: List, similar_spacing: List, total_files: int) -> Dict:
    """Estimate design debt in hours."""
    # Each color consolidation: 0.5 hours
    color_debt = len(similar_colors) * 0.5

    # Each spacing consolidation: 0.25 hours
    spacing_debt = len(similar_spacing) * 0.25

    # Additional debt for files needing review
    file_review = total_files * 0.05

    total_hours = color_debt + spacing_debt + file_review

    return {
        'color_consolidation_hours': color_debt,
        'spacing_consolidation_hours': spacing_debt,
        'file_review_hours': round(file_review, 1),
        'total_hours': round(total_hours, 1),
        'estimated_cost': round(total_hours * 50, 2)  # $50/hour
    }

# === REPORT GENERATION ===

def format_markdown_report(project_data: Dict, token_usage: Dict, similar_colors: List,
                           similar_spacing: List, consistency: Tuple[float, str],
                           design_debt: Dict) -> str:
    """Format analysis as Markdown report."""
    lines = [
        "# CascadeMap Report",
        "",
        f"**Project:** {project_data['project']}",
        f"**Analyzed:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Files Scanned:** {project_data['total_files']}",
        "",
        "---",
        "",
        "## Design Consistency",
        "",
        f"| Metric | Value |",
        f"|---------|-------|",
        f"| **Consistency Score** | **{consistency[0]}/100 ({consistency[1]})** |",
        f"| Unique Colors | {len([k for k,v in token_usage.items() if v['type'] == 'color'])} |",
        f"| Unique Spacing Values | {len([k for k,v in token_usage.items() if v['type'] == 'spacing'])} |",
        f"| Total Token Usages | {sum(v['count'] for v in token_usage.values())} |",
        "",
    ]

    # Top tokens
    top_tokens = sorted(token_usage.items(), key=lambda x: x[1]['count'], reverse=True)[:10]
    if top_tokens:
        lines.append("## Most Used Tokens")
        lines.append("")
        lines.append("| Token | Type | Usages | Files |")
        lines.append("|-------|------|--------|-------|")
        for token, data in top_tokens:
            lines.append(f"| `{token}` | {data['type']} | {data['count']} | {data['file_count']} |")
        lines.append("")

    # Similar colors
    if similar_colors:
        lines.append("## Similar Colors (Consider Consolidating)")
        lines.append("")
        for group in similar_colors:
            lines.append(f"- {', '.join(f'`{c}`' for c in group)}")
            # Show usage context
            for color in group[:3]:
                if color in token_usage:
                    files = token_usage[color]['files'][:2]
                    lines.append(f"  - `{color}` used in {token_usage[color]['file_count']} files")
        lines.append("")

    # Similar spacing
    if similar_spacing:
        lines.append("## Similar Spacing Values (Consider Consolidating)")
        lines.append("")
        for group in similar_spacing:
            px_values = [f"{spacing_normalize(s):.0f}px" for s in group]
            lines.append(f"- **{', '.join(group)}** ({', '.join(px_values)})")
        lines.append("")

    # Design debt
    lines.append("## Design Debt")
    lines.append("")
    lines.append(f"| Source | Hours |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Color consolidation | {design_debt['color_consolidation_hours']} |")
    lines.append(f"| Spacing consolidation | {design_debt['spacing_consolidation_hours']} |")
    lines.append(f"| File review | {design_debt['file_review_hours']} |")
    lines.append(f"| **Total** | **{design_debt['total_hours']} hours** |")
    lines.append(f"| **Estimated Cost** | **${design_debt['estimated_cost']}** |")
    lines.append("")

    # Cascades
    lines.append("## High-Impact Tokens")
    lines.append("")
    high_impact = [k for k, v in token_usage.items() if v['file_count'] >= 5]
    if high_impact:
        high_impact.sort(key=lambda x: token_usage[x]['file_count'], reverse=True)
        for token in high_impact[:5]:
            data = token_usage[token]
            lines.append(f"- `{token}` ({data['type']})")
            lines.append(f"  - Used in {data['file_count']} files, {data['count']} times")
            lines.append(f"  - Impact: {'HIGH' if data['file_count'] >= 10 else 'MEDIUM'}")
        lines.append("")
    else:
        lines.append("No high-impact tokens found (tokens used in 5+ files).")
        lines.append("")

    lines.append("---")
    lines.append(f"*Generated by CascadeMap v1.0*")

    return '\n'.join(lines)

def format_telegram_summary(project_data: Dict, consistency: Tuple[float, str],
                            similar_colors: List, similar_spacing: List,
                            design_debt: Dict) -> str:
    """Format summary for Telegram."""
    lines = [
        "🎨 CascadeMap Report",
        "━━━━━━━━━━━━━━━━━━━━━━",
        f"Project: {project_data['project']}",
        f"Files: {project_data['total_files']}",
        "",
        f"Consistency: {consistency[0]}/100 ({consistency[1]})",
        f"Design Debt: {design_debt['total_hours']}h (${design_debt['estimated_cost']})",
        "",
    ]

    if similar_colors:
        lines.append(f"Similar colors: {len(similar_colors)} groups")
    if similar_spacing:
        lines.append(f"Similar spacing: {len(similar_spacing)} groups")

    return '\n'.join(lines)

# === OUTPUT ===

def save_report(content: str, file_path: str) -> bool:
    """Save report to file."""
    try:
        os.makedirs(os.path.dirname(file_path) or '.', exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error saving {file_path}: {e}")
        return False

def send_telegram(message: str) -> bool:
    """Send message to Telegram."""
    try:
        import requests
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
        chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')

        if not bot_token or not chat_id:
            return False

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        response = requests.post(url, json={
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }, timeout=30)
        return response.status_code == 200
    except Exception:
        return False

# === MAIN ===

def main():
    parser = argparse.ArgumentParser(description='CascadeMap - Design System Cascade Tracker')
    parser.add_argument('--path', '-p', required=True, help='Project path to analyze')
    parser.add_argument('--output', '-o', default='./cascade-report.md', help='Output file')
    parser.add_argument('--report', '-r', action='store_true', help='Generate full report')
    parser.add_argument('--find-inconsistencies', '-f', action='store_true', help='Find inconsistencies only')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--find', help='Find specific token usage')

    args = parser.parse_args()

    print(f"Analyzing: {args.path}")
    project_data = analyze_project(args.path)

    if 'error' in project_data:
        print(f"ERROR: {project_data['error']}")
        sys.exit(1)

    # Build token usage map
    token_usage = build_token_usage_map(project_data['all_tokens'])

    # Find similarities
    similar_colors = find_similar_colors(token_usage)
    similar_spacing = find_similar_spacing(token_usage)

    # Calculate scores
    consistency = calculate_consistency_score(token_usage, similar_colors, similar_spacing)
    design_debt = estimate_design_debt(similar_colors, similar_spacing, project_data['total_files'])

    if args.json:
        output = {
            'project': project_data,
            'token_usage': token_usage,
            'similar_colors': similar_colors,
            'similar_spacing': similar_spacing,
            'consistency': {'score': consistency[0], 'rating': consistency[1]},
            'design_debt': design_debt
        }
        print(json.dumps(output, indent=2))
        return

    # Find specific token
    if args.find:
        if args.find in token_usage:
            data = token_usage[args.find]
            print(f"\nToken: {args.find}")
            print(f"Type: {data['type']}")
            print(f"Usages: {data['count']}")
            print(f"Files: {data['file_count']}")
            for f in data['files']:
                print(f"  - {f}")
        else:
            print(f"Token '{args.find}' not found")
        return

    # Inconsistencies only
    if args.find_inconsistencies:
        print("\n## Inconsistencies Found\n")

        if similar_colors:
            print(f"Similar Colors ({len(similar_colors)} groups):")
            for group in similar_colors:
                print(f"  - {', '.join(group)}")
        else:
            print("No similar colors found.")

        if similar_spacing:
            print(f"\nSimilar Spacing ({len(similar_spacing)} groups):")
            for group in similar_spacing:
                px_values = [f"{spacing_normalize(s):.0f}px" for s in group]
                print(f"  - {', '.join(group)} ({', '.join(px_values)})")
        else:
            print("No similar spacing found.")

        print(f"\nDesign Debt: {design_debt['total_hours']} hours (${design_debt['estimated_cost']})")
        return

    # Full report
    report = format_markdown_report(
        project_data, token_usage, similar_colors, similar_spacing,
        consistency, design_debt
    )

    if args.report:
        print(report)

        # Save to file
        if save_report(report, args.output):
            print(f"\nReport saved to: {args.output}")

        # Send to Telegram
        summary = format_telegram_summary(project_data, consistency, similar_colors,
                                          similar_spacing, design_debt)
        send_telegram(summary)
    else:
        # Quick summary
        print(f"\nConsistency Score: {consistency[0]}/100 ({consistency[1]})")
        print(f"Unique Colors: {len([k for k,v in token_usage.items() if v['type'] == 'color'])}")
        print(f"Similar Colors: {len(similar_colors)} groups")
        print(f"Similar Spacing: {len(similar_spacing)} groups")
        print(f"Design Debt: {design_debt['total_hours']} hours")

        print("\nUse --report for full analysis")

if __name__ == '__main__':
    main()