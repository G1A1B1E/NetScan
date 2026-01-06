#!/usr/bin/env python3
"""
Export Helper - Fast data export operations
Supports CSV, JSON, HTML, and formatted text exports
"""

import sys
import csv
import json
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional
from io import StringIO
import html


def to_csv(data: List[Dict[str, Any]], fields: Optional[List[str]] = None, 
           include_header: bool = True) -> str:
    """Convert list of dicts to CSV string"""
    if not data:
        return ""
    
    # Auto-detect fields from first record if not specified
    if not fields:
        fields = list(data[0].keys())
    
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction='ignore')
    
    if include_header:
        writer.writeheader()
    
    writer.writerows(data)
    return output.getvalue()


def to_json(data: Any, pretty: bool = True, sort_keys: bool = False) -> str:
    """Convert data to JSON string"""
    indent = 2 if pretty else None
    return json.dumps(data, indent=indent, sort_keys=sort_keys, default=str)


def to_html_table(data: List[Dict[str, Any]], fields: Optional[List[str]] = None,
                  title: Optional[str] = None, css_class: str = "data-table",
                  include_style: bool = True) -> str:
    """Convert list of dicts to HTML table"""
    if not data:
        return "<p>No data</p>"
    
    # Auto-detect fields
    if not fields:
        fields = list(data[0].keys())
    
    lines = []
    
    # Optional embedded CSS
    if include_style:
        lines.append("""<style>
.data-table {
    border-collapse: collapse;
    width: 100%;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    font-size: 14px;
}
.data-table th, .data-table td {
    border: 1px solid #ddd;
    padding: 8px 12px;
    text-align: left;
}
.data-table th {
    background-color: #4a90d9;
    color: white;
    font-weight: 600;
}
.data-table tr:nth-child(even) {
    background-color: #f9f9f9;
}
.data-table tr:hover {
    background-color: #f1f1f1;
}
.data-table .mac {
    font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
    font-size: 13px;
}
.data-table .ip {
    font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
}
.data-table-title {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 10px;
    color: #333;
}
.data-table-info {
    font-size: 12px;
    color: #666;
    margin-top: 8px;
}
</style>""")
    
    if title:
        lines.append(f'<div class="data-table-title">{html.escape(title)}</div>')
    
    lines.append(f'<table class="{css_class}">')
    
    # Header
    lines.append('  <thead>')
    lines.append('    <tr>')
    for field in fields:
        display_name = field.replace('_', ' ').title()
        lines.append(f'      <th>{html.escape(display_name)}</th>')
    lines.append('    </tr>')
    lines.append('  </thead>')
    
    # Body
    lines.append('  <tbody>')
    for row in data:
        lines.append('    <tr>')
        for field in fields:
            value = row.get(field, '')
            cell_class = ''
            
            # Auto-detect special fields for styling
            if field.lower() in ['mac', 'mac_address', 'macaddress']:
                cell_class = ' class="mac"'
            elif field.lower() in ['ip', 'ip_address', 'ipaddress']:
                cell_class = ' class="ip"'
            
            lines.append(f'      <td{cell_class}>{html.escape(str(value))}</td>')
        lines.append('    </tr>')
    lines.append('  </tbody>')
    
    lines.append('</table>')
    
    # Footer info
    lines.append(f'<div class="data-table-info">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | {len(data)} records</div>')
    
    return '\n'.join(lines)


def to_html_document(content: str, title: str = "Export") -> str:
    """Wrap content in full HTML document"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)}</title>
</head>
<body>
{content}
</body>
</html>"""


def to_markdown_table(data: List[Dict[str, Any]], fields: Optional[List[str]] = None) -> str:
    """Convert list of dicts to Markdown table"""
    if not data:
        return "No data"
    
    if not fields:
        fields = list(data[0].keys())
    
    lines = []
    
    # Header
    headers = [f.replace('_', ' ').title() for f in fields]
    lines.append('| ' + ' | '.join(headers) + ' |')
    lines.append('| ' + ' | '.join(['---'] * len(fields)) + ' |')
    
    # Rows
    for row in data:
        values = [str(row.get(f, '')) for f in fields]
        lines.append('| ' + ' | '.join(values) + ' |')
    
    return '\n'.join(lines)


def to_text_table(data: List[Dict[str, Any]], fields: Optional[List[str]] = None,
                  border: bool = True) -> str:
    """Convert list of dicts to formatted text table"""
    if not data:
        return "No data"
    
    if not fields:
        fields = list(data[0].keys())
    
    # Calculate column widths
    headers = [f.replace('_', ' ').title() for f in fields]
    widths = [len(h) for h in headers]
    
    for row in data:
        for i, field in enumerate(fields):
            value = str(row.get(field, ''))
            widths[i] = max(widths[i], len(value))
    
    # Add padding
    widths = [w + 2 for w in widths]
    
    lines = []
    
    if border:
        # Top border
        lines.append('┌' + '┬'.join('─' * w for w in widths) + '┐')
        
        # Header
        header_cells = [f' {headers[i].ljust(widths[i] - 2)} ' for i in range(len(headers))]
        lines.append('│' + '│'.join(header_cells) + '│')
        
        # Header separator
        lines.append('├' + '┼'.join('─' * w for w in widths) + '┤')
        
        # Data rows
        for row in data:
            cells = []
            for i, field in enumerate(fields):
                value = str(row.get(field, ''))
                cells.append(f' {value.ljust(widths[i] - 2)} ')
            lines.append('│' + '│'.join(cells) + '│')
        
        # Bottom border
        lines.append('└' + '┴'.join('─' * w for w in widths) + '┘')
    else:
        # Simple format without box drawing
        header_line = '  '.join(h.ljust(widths[i]) for i, h in enumerate(headers))
        lines.append(header_line)
        lines.append('-' * len(header_line))
        
        for row in data:
            cells = []
            for i, field in enumerate(fields):
                value = str(row.get(field, ''))
                cells.append(value.ljust(widths[i]))
            lines.append('  '.join(cells))
    
    return '\n'.join(lines)


def to_shell_vars(data: Dict[str, Any], prefix: str = "") -> str:
    """Convert dict to shell variable assignments"""
    lines = []
    for key, value in data.items():
        var_name = f"{prefix}{key}".upper().replace('-', '_').replace(' ', '_')
        
        if isinstance(value, (list, dict)):
            value = json.dumps(value)
        elif isinstance(value, bool):
            value = "true" if value else "false"
        
        # Escape single quotes for shell
        value = str(value).replace("'", "'\\''")
        lines.append(f"{var_name}='{value}'")
    
    return '\n'.join(lines)


def from_csv(content: str, has_header: bool = True) -> List[Dict[str, Any]]:
    """Parse CSV content to list of dicts"""
    reader = csv.reader(StringIO(content))
    rows = list(reader)
    
    if not rows:
        return []
    
    if has_header:
        headers = rows[0]
        return [dict(zip(headers, row)) for row in rows[1:]]
    else:
        # Generate column names
        num_cols = len(rows[0])
        headers = [f"col{i+1}" for i in range(num_cols)]
        return [dict(zip(headers, row)) for row in rows]


def from_json(content: str) -> Any:
    """Parse JSON content"""
    return json.loads(content)


def merge_records(records: List[Dict[str, Any]], key_field: str) -> List[Dict[str, Any]]:
    """Merge records with same key, combining fields"""
    merged = {}
    
    for record in records:
        key = record.get(key_field)
        if key is None:
            continue
        
        if key not in merged:
            merged[key] = record.copy()
        else:
            # Update with new values (non-empty only)
            for k, v in record.items():
                if v and (k not in merged[key] or not merged[key][k]):
                    merged[key][k] = v
    
    return list(merged.values())


def filter_records(records: List[Dict[str, Any]], field: str, 
                   pattern: str, inverse: bool = False) -> List[Dict[str, Any]]:
    """Filter records by field value containing pattern"""
    import re
    regex = re.compile(pattern, re.IGNORECASE)
    
    result = []
    for record in records:
        value = str(record.get(field, ''))
        match = bool(regex.search(value))
        
        if (match and not inverse) or (not match and inverse):
            result.append(record)
    
    return result


def sort_records(records: List[Dict[str, Any]], field: str, 
                 reverse: bool = False) -> List[Dict[str, Any]]:
    """Sort records by field"""
    return sorted(records, key=lambda x: str(x.get(field, '')), reverse=reverse)


def select_fields(records: List[Dict[str, Any]], fields: List[str]) -> List[Dict[str, Any]]:
    """Select only specified fields from records"""
    return [{k: r.get(k) for k in fields} for r in records]


def count_by_field(records: List[Dict[str, Any]], field: str) -> Dict[str, int]:
    """Count records grouped by field value"""
    counts = {}
    for record in records:
        value = str(record.get(field, 'Unknown'))
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))


def main():
    parser = argparse.ArgumentParser(
        description='Export Helper - Fast data export operations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --to csv < data.json                 # JSON to CSV
  %(prog)s --to json < data.csv                 # CSV to JSON
  %(prog)s --to html --title "Devices" < data.json  # JSON to HTML table
  %(prog)s --to markdown < data.json            # JSON to Markdown table
  %(prog)s --to table < data.json               # JSON to text table
  %(prog)s --filter mac "aa:bb" < data.json     # Filter records
  %(prog)s --sort ip < data.json                # Sort by field
  %(prog)s --count vendor < data.json           # Count by field
  %(prog)s --select mac,ip,vendor < data.json   # Select fields only
        """
    )
    
    parser.add_argument('--to', '-t', choices=['csv', 'json', 'html', 'markdown', 'table', 'shell'],
                        default='json', help='Output format (default: json)')
    parser.add_argument('--from', '-f', dest='input_format', choices=['csv', 'json', 'auto'],
                        default='auto', help='Input format (default: auto-detect)')
    parser.add_argument('--title', help='Title for HTML output')
    parser.add_argument('--fields', help='Comma-separated list of fields to include')
    parser.add_argument('--no-header', action='store_true', help='CSV has no header')
    parser.add_argument('--pretty', action='store_true', default=True, help='Pretty print output')
    parser.add_argument('--compact', action='store_true', help='Compact output (no pretty print)')
    parser.add_argument('--full-html', action='store_true', help='Output complete HTML document')
    parser.add_argument('--no-border', action='store_true', help='Text table without borders')
    
    # Operations
    parser.add_argument('--filter', nargs=2, metavar=('FIELD', 'PATTERN'),
                        help='Filter records by field pattern')
    parser.add_argument('--exclude', nargs=2, metavar=('FIELD', 'PATTERN'),
                        help='Exclude records by field pattern')
    parser.add_argument('--sort', metavar='FIELD', help='Sort by field')
    parser.add_argument('--reverse', action='store_true', help='Reverse sort order')
    parser.add_argument('--select', metavar='FIELDS', help='Select only these fields (comma-separated)')
    parser.add_argument('--merge', metavar='KEY', help='Merge records with same key field')
    parser.add_argument('--count', metavar='FIELD', help='Count records by field')
    
    args = parser.parse_args()
    
    # Read input
    content = sys.stdin.read()
    if not content.strip():
        print("No input data", file=sys.stderr)
        return 1
    
    # Detect/parse input format
    data = None
    if args.input_format == 'json' or (args.input_format == 'auto' and content.strip().startswith(('[', '{'))):
        try:
            data = from_json(content)
            if isinstance(data, dict):
                data = [data]
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}", file=sys.stderr)
            return 1
    else:
        data = from_csv(content, has_header=not args.no_header)
    
    if not data:
        print("No data parsed", file=sys.stderr)
        return 1
    
    # Apply operations
    if args.filter:
        data = filter_records(data, args.filter[0], args.filter[1])
    
    if args.exclude:
        data = filter_records(data, args.exclude[0], args.exclude[1], inverse=True)
    
    if args.merge:
        data = merge_records(data, args.merge)
    
    if args.sort:
        data = sort_records(data, args.sort, args.reverse)
    
    if args.select:
        fields = [f.strip() for f in args.select.split(',')]
        data = select_fields(data, fields)
    
    # Count operation (outputs different format)
    if args.count:
        counts = count_by_field(data, args.count)
        if args.to == 'json':
            print(to_json(counts, pretty=not args.compact))
        else:
            for value, count in counts.items():
                print(f"{value}: {count}")
        return 0
    
    # Parse fields argument
    fields = None
    if args.fields:
        fields = [f.strip() for f in args.fields.split(',')]
    
    # Generate output
    pretty = not args.compact
    
    if args.to == 'csv':
        output = to_csv(data, fields)
    elif args.to == 'json':
        output = to_json(data, pretty=pretty)
    elif args.to == 'html':
        output = to_html_table(data, fields, title=args.title)
        if args.full_html:
            output = to_html_document(output, title=args.title or "Export")
    elif args.to == 'markdown':
        output = to_markdown_table(data, fields)
    elif args.to == 'table':
        output = to_text_table(data, fields, border=not args.no_border)
    elif args.to == 'shell':
        if len(data) == 1:
            output = to_shell_vars(data[0])
        else:
            print("Shell output requires single record", file=sys.stderr)
            return 1
    else:
        output = to_json(data)
    
    print(output)
    return 0


if __name__ == '__main__':
    sys.exit(main())
