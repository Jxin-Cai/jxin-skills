import re
import json
import sys
import os
import argparse

import base64

import base64
import subprocess
import tempfile

def parse_args():
    parser = argparse.ArgumentParser(description='Convert Markdown to HTML with inline styles.')
    parser.add_argument('input_file', help='Path to the input markdown file')
    parser.add_argument('--theme', default='thoughtworks', help='Name of the theme to use (default: thoughtworks)')
    return parser.parse_args()

def load_theme(theme_name):
    # Look for theme in the themes directory relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    theme_path = os.path.join(script_dir, '..', 'themes', f'{theme_name}.json')
    
    if not os.path.exists(theme_path):
        print(f"Warning: Theme file not found at {theme_path}. Using empty theme.")
        return {}
    
    with open(theme_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_mmdc_path():
    # First, try to find mmdc in system PATH
    try:
        result = subprocess.run(['which', 'mmdc'], capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            mmdc_path = result.stdout.strip()
            if mmdc_path and os.path.exists(mmdc_path):
                return mmdc_path
    except:
        pass
    
    # Fallback: Attempt to find mmdc in the skill's node_modules
    script_dir = os.path.dirname(os.path.abspath(__file__))
    mmdc_path = os.path.join(script_dir, '..', 'node_modules', '.bin', 'mmdc')
    if os.path.exists(mmdc_path):
        return mmdc_path
    
    return None

def apply_style(tag, content, theme, extra_attrs=""):
    style = theme.get(tag, "")
    if style:
        return f'<{tag} style="{style}" {extra_attrs}>{content}</{tag}>'
    return f'<{tag} {extra_attrs}>{content}</{tag}>'

def is_local_image(path):
    """Check if the image path is a local file (not a URL)."""
    return not (path.startswith('http://') or path.startswith('https://') or path.startswith('data:'))

def get_image_mime_type(file_path):
    """Determine MIME type based on file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    mime_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.svg': 'image/svg+xml',
        '.bmp': 'image/bmp',
    }
    return mime_types.get(ext, 'image/png')

def convert_local_image_to_base64(img_path, input_file_dir):
    """Convert a local image to base64 data URI."""
    # Handle relative paths
    if not os.path.isabs(img_path):
        img_path = os.path.join(input_file_dir, img_path)
    
    # Normalize path
    img_path = os.path.normpath(img_path)
    
    if not os.path.exists(img_path):
        print(f"Warning: Image file not found: {img_path}")
        return None
    
    try:
        with open(img_path, 'rb') as f:
            img_data = f.read()
        
        mime_type = get_image_mime_type(img_path)
        encoded_img = base64.b64encode(img_data).decode('ascii')
        return f"data:{mime_type};base64,{encoded_img}"
    except Exception as e:
        print(f"Warning: Failed to convert image {img_path}: {e}")
        return None

def get_mermaid_image_size(mermaid_code):
    """
    Determine appropriate image size based on Mermaid diagram complexity.
    Returns max-width in pixels.
    
    Strategy:
    1. Detect diagram type (flowchart, sequence, gantt, class, state, etc.)
    2. Count elements (nodes/participants/states/classes/tasks)
    3. Count relationships (connections/messages/transitions)
    4. Calculate complexity score = elements * 2 + relationships
    
    Rules:
    - Simple diagrams (score ≤ 12): 300px
    - Medium diagrams (score 13-30): 600px
    - Complex diagrams (score > 30): 900px
    """
    import re
    
    lines = [line.strip() for line in mermaid_code.split('\n') if line.strip() and not line.strip().startswith('%%')]
    
    if not lines:
        return 300
    
    # Detect diagram type
    first_line = lines[0].lower()
    
    element_count = 0
    relationship_count = 0
    
    # === Sequence Diagram ===
    if 'sequencediagram' in first_line or 'sequenceDiagram' in mermaid_code:
        # Count participants
        for line in lines:
            if re.match(r'^\s*participant\s+', line):
                element_count += 1
        
        # Count messages/interactions
        message_patterns = [r'->>', r'-->>', r'->', r'-->', r'-x', r'--x', r'-\)', r'--\)']
        for line in lines:
            for pattern in message_patterns:
                relationship_count += len(re.findall(pattern, line))
    
    # === Gantt Chart ===
    elif 'gantt' in first_line:
        # Count sections
        for line in lines:
            if re.match(r'^\s*section\s+', line):
                element_count += 1
        
        # Count tasks (lines with dates or task definitions)
        for line in lines:
            if ':' in line and not line.strip().startswith('section'):
                relationship_count += 1
    
    # === Class Diagram ===
    elif 'classdiagram' in first_line or 'classDiagram' in mermaid_code:
        # Count classes
        for line in lines:
            if re.match(r'^\s*class\s+', line):
                element_count += 1
        
        # Count relationships
        relationship_patterns = [r'<\|--', r'\*--', r'o--', r'<\.\.|>', r'-->', r'<--', r'\.\.|>']
        for line in lines:
            for pattern in relationship_patterns:
                relationship_count += len(re.findall(pattern, line))
    
    # === State Diagram ===
    elif 'statediagram' in first_line or 'stateDiagram' in mermaid_code:
        # Count states
        for line in lines:
            if re.match(r'^\s*state\s+', line):
                element_count += 1
        
        # Count transitions
        for line in lines:
            if '-->' in line:
                relationship_count += 1
    
    # === Flowchart (default) ===
    else:
        # Flowchart nodes: A[text], B(text), C{text}, D((text)), E>text], F[/text/], etc.
        node_patterns = [
            r'\b[A-Za-z0-9_]+\[',      # A[text], start[text]
            r'\b[A-Za-z0-9_]+\(',      # A(text)
            r'\b[A-Za-z0-9_]+\{',      # A{text}
            r'\b[A-Za-z0-9_]+\(\(',    # A((text))
            r'\b[A-Za-z0-9_]+\>',      # A>text]
            r'\b[A-Za-z0-9_]+\[/',     # A[/text/]
        ]
        
        seen_nodes = set()
        for line in lines:
            for pattern in node_patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    node_id = re.match(r'([A-Za-z0-9_]+)', match)
                    if node_id:
                        seen_nodes.add(node_id.group(1))
        
        element_count = len(seen_nodes)
        
        # Count connections
        connection_patterns = [r'-->', r'---', r'-\.->', r'-\.', r'==>', r'===']
        for line in lines:
            for pattern in connection_patterns:
                relationship_count += len(re.findall(pattern, line))
    
    # Calculate complexity score
    # Elements are more important (weight 2), relationships are secondary (weight 1)
    complexity_score = element_count * 2 + relationship_count
    
    # Determine size based on complexity
    if complexity_score <= 10:
        return 300
    elif complexity_score <= 30:
        return 450
    elif complexity_score <= 50:
        return 600
    else:
        return 900

def convert_markdown(text, theme, input_file_dir='.'):
    html_lines = []
    lines = text.split('\n')
    in_code_block = False
    code_block_lang = ""
    code_block_content = []
    in_list = False
    list_items = []
    in_table = False
    table_lines = []
    
    mmdc_path = get_mmdc_path()
    if not mmdc_path:
        print("Warning: local mermaid-cli (mmdc) not found. Mermaid diagrams may fail to render correctly if fallback is needed.")

    # Pre-process theme styles
    style_h1 = theme.get('h1', '')
    style_h2 = theme.get('h2', '')
    style_h3 = theme.get('h3', '')
    style_h4 = theme.get('h4', 'font-size: 1.25em; font-weight: bold; margin-top: 1em; margin-bottom: 0.5em;')
    style_h5 = theme.get('h5', 'font-size: 1.1em; font-weight: bold; margin-top: 1em; margin-bottom: 0.5em;')
    style_h6 = theme.get('h6', 'font-size: 1em; font-weight: bold; margin-top: 1em; margin-bottom: 0.5em;')
    style_hr = theme.get('hr', 'border: none; border-top: 2px solid #ddd; margin: 2em 0;')
    style_p = theme.get('p', '')
    style_blockquote = theme.get('blockquote', '')
    style_code_wrapper = theme.get('code_block_wrapper', '')
    style_code = theme.get('code', '')
    style_img = theme.get('img', '')
    style_ul = theme.get('ul', 'margin-top: 0px; margin-bottom: 1rem; list-style-type: disc; padding-left: 2em; list-style-position: outside;')
    style_li = theme.get('li', 'display: list-item; margin-bottom: 0.5em; line-height: 1.6; padding-left: 0.5em;')
    style_table = theme.get('table', 'border-collapse: collapse; width: 100%; margin: 1em 0;')
    style_th = theme.get('th', 'border: 1px solid #ddd; padding: 8px; background-color: #f2f2f2; text-align: left;')
    style_td = theme.get('td', 'border: 1px solid #ddd; padding: 8px;')
    
    def process_inline(line):
        # Prefix with zero-width space in span to prevent copy-paste newline issues
        zwsp_span = '<span>&#8203;</span>'
        
        # Bold
        line = re.sub(r'\*\*(.*?)\*\*', f'{zwsp_span}<strong>\\1</strong>', line)
        # Italic
        line = re.sub(r'\*(.*?)\*', f'{zwsp_span}<em>\\1</em>', line)
        # Inline code
        line = re.sub(r'`(.*?)`', f'{zwsp_span}<code style="background-color: rgba(175, 184, 193, 0.2); padding: 0.2em 0.4em; border-radius: 6px; font-family: monospace;">\\1</code>', line)
        
        # Images - convert local images to base64
        def process_image(match):
            alt_text = match.group(1)
            img_src = match.group(2)
            
            # Check if it's a local image
            if is_local_image(img_src):
                base64_src = convert_local_image_to_base64(img_src, input_file_dir)
                if base64_src:
                    img_src = base64_src
                    print(f"Converted local image to base64: {match.group(2)}")
                else:
                    print(f"Failed to convert image, keeping original path: {match.group(2)}")
            
            return f'<img src="{img_src}" alt="{alt_text}" style="{style_img}">'
        
        # Process images first (before colon handling)
        line = re.sub(r'!\[(.*?)\]\((.*?)\)', process_image, line)
        
        # Links
        line = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', line)
        
        # Post-process: Ensure non-breaking space after closing tags followed by colon
        # Handles both ": " and ":" (no space)
        line = re.sub(r'(</strong>|</em>|</code>):(\s*)', r'\1:&nbsp;', line)
        
        # Prevent line breaks after colons by inserting Zero Width Joiner (ZWJ)
        # This handles both Chinese colon (：) and English colon (:) in plain text
        # ZWJ (U+200D, &#8205;) prevents unwanted line breaks in rich text editors
        # IMPORTANT: Negative lookahead to avoid matching colons inside HTML tags (e.g., src="data:image/png")
        line = re.sub(r'([：:])(?![^<]*>)(\s)', r'\1&#8205;\2', line)  # colon + space (not inside tags)
        line = re.sub(r'([：:])(?![^<]*>)([^\s<&#])', r'\1&#8205;\2', line)  # colon + non-space/non-tag
        
        return line

    # List processing with nesting support
    def get_indent(line):
        return len(line) - len(line.lstrip())

    def flush_list():
        nonlocal in_list, list_items
        if in_list and list_items:
            # list_items contains tuples: (indent_level, content)
            # We normalize indents to levels (0, 1, 2...)
            if not list_items:
                return
            
            # Group items by level
            # Strategy: Generate HTML directly using a recursive approach or stack
            # Base indent
            base_indent = list_items[0][0]
            
            # Stack of open lists: (indent_level, is_closed)
            # Actually we just need to manage <ul> tags
            
            current_indent = -1
            
            # To produce valid HTML: <ul><li>Item... <ul><li>Nested</li></ul></li></ul>
            # We need to buffer the HTML
            
            html_stack = [] # Stack of "<ul>"
            
            # Determine levels based on indentation changes
            # We map explicit indent values to abstract levels
            # But simpler: just open/close UL based on indent increase/decrease
            
            # New approach:
            # Iterate items. 
            # If indent > prev: Open <ul>
            # If indent < prev: Close <ul>(s)
            # Same indent: Close previous <li>, Open new <li>
            
            # We need to normalize indentation first because sometimes users use 2 spaces, sometimes 4
            # But relative indentation is what matters
            
            active_indents = [] # Stack of indentation values associated with open <ul>s
            
            # Helper to close lists until matching indent
            def close_lists_until(target_indent):
                closed_count = 0
                while active_indents and active_indents[-1] > target_indent:
                    html_lines.append(f'</li></ul>')
                    active_indents.pop()
                    closed_count += 1
                return closed_count

            # Helper to open list
            def open_list(indent):
                html_lines.append(f'<ul style="{style_ul}">')
                active_indents.append(indent)

            for i, (indent, content) in enumerate(list_items):
                if i == 0:
                    open_list(indent)
                    html_lines.append(f'<li style="{style_li}">{content}')
                else:
                    prev_indent = list_items[i-1][0]
                    
                    if indent > prev_indent:
                        # Nested list
                        # The previous LI is still open, so we open a UL inside it
                        open_list(indent)
                        html_lines.append(f'<li style="{style_li}">{content}')
                    elif indent < prev_indent:
                        # Close nested lists
                        close_lists_until(indent)
                        # Close previous item
                        html_lines.append('</li>') 
                        
                        if not active_indents: # Should not happen if indented correctly relative to root, but safe-guard
                             open_list(indent)

                        html_lines.append(f'<li style="{style_li}">{content}')
                    else:
                        # Same level
                        # Close previous LI
                        html_lines.append('</li>') # Close previous sibling
                        html_lines.append(f'<li style="{style_li}">{content}')
            
            # Close all remaining open lists
            while active_indents:
                html_lines.append('</li></ul>')
                active_indents.pop()

            list_items = []
            in_list = False
    
    def flush_table():
        nonlocal in_table, table_lines
        if in_table and table_lines:
            html_lines.append(f'<table style="{style_table}">')
            for i, row in enumerate(table_lines):
                if i == 1 and all(cell.strip().replace('-', '').replace('|', '').replace(':', '') == '' for cell in row):
                    continue  # Skip separator line
                cells = [cell.strip() for cell in row.split('|')[1:-1]]  # Remove empty first/last
                tag = 'th' if i == 0 else 'td'
                style = style_th if i == 0 else style_td
                html_lines.append('  <tr>')
                for cell in cells:
                    html_lines.append(f'    <{tag} style="{style}">{process_inline(cell)}</{tag}>')
                html_lines.append('  </tr>')
            html_lines.append('</table>')
            table_lines = []
            in_table = False

    for line in lines:
        # Code Blocks
        if line.strip().startswith('```'):
            flush_list()
            flush_table()
            if in_code_block:
                # End of code block
                code_content = '\n'.join(code_block_content)
                
                if code_block_lang == 'mermaid':
                    # Try to generate static image first (better for copy-paste)
                    if mmdc_path:
                        try:
                            # Use temp files for input/output
                            with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False, encoding='utf-8') as tmp_in:
                                tmp_in.write(code_content)
                                tmp_in_path = tmp_in.name
                            
                            tmp_out_path = tmp_in_path + '.png'
                            
                            # Run mmdc to generate PNG (better for rich text editors)
                            # Use --scale to increase resolution for better clarity
                            subprocess.run([mmdc_path, '-i', tmp_in_path, '-o', tmp_out_path, '-b', 'white', '--scale', '3'], 
                                         check=True, capture_output=True, text=True)
                            
                            # Read PNG and embed as base64
                            if os.path.exists(tmp_out_path):
                                with open(tmp_out_path, 'rb') as f_png:
                                    png_content = f_png.read()
                                
                                # Convert to base64 for embedding
                                encoded_png = base64.b64encode(png_content).decode('ascii')
                                img_src = f"data:image/png;base64,{encoded_png}"
                                
                                # Determine image size based on diagram complexity
                                mermaid_size = get_mermaid_image_size(code_content)
                                mermaid_style = f"max-width: {mermaid_size}px; height: auto; display: block; margin: 1rem auto;"
                                html_lines.append(f'<div style="text-align: center;"><img src="{img_src}" alt="Mermaid Diagram" style="{mermaid_style}"></div>')
                                
                                os.remove(tmp_out_path)
                            else:
                                # Fallback to client-side rendering
                                escaped_content = code_content.replace('<', '&lt;').replace('>', '&gt;')
                                html_lines.append(f'<div class="mermaid">{escaped_content}</div>')
                                
                            os.remove(tmp_in_path)
                            
                        except Exception as e:
                            print(f"mmdc failed: {e}, falling back to client-side rendering")
                            # Fallback to client-side rendering
                            escaped_content = code_content.replace('<', '&lt;').replace('>', '&gt;')
                            html_lines.append(f'<div class="mermaid">{escaped_content}</div>')
                    else:
                        # No mmdc available, use client-side rendering
                        print("mmdc not found, using client-side rendering")
                        escaped_content = code_content.replace('<', '&lt;').replace('>', '&gt;')
                        html_lines.append(f'<div class="mermaid">{escaped_content}</div>')

                else:
                    # Regular code block
                    # Escape HTML characters
                    code_content = code_content.replace('<', '&lt;').replace('>', '&gt;')
                    
                    # Preserve formatting: convert spaces to prevent collapse in rich text editors
                    # Strategy: Replace leading spaces with &nbsp; and alternate &nbsp; with space for consecutive spaces
                    def preserve_spaces(text):
                        """Convert spaces to &nbsp; pattern to prevent collapse while keeping text selectable."""
                        result = []
                        i = 0
                        while i < len(text):
                            if text[i] == ' ':
                                # Count consecutive spaces
                                space_count = 0
                                while i < len(text) and text[i] == ' ':
                                    space_count += 1
                                    i += 1
                                
                                # Convert to alternating pattern: &nbsp; space &nbsp; space...
                                # This prevents collapse while keeping selectability
                                for j in range(space_count):
                                    if j % 2 == 0:
                                        result.append('&nbsp;')
                                    else:
                                        result.append(' ')
                            else:
                                result.append(text[i])
                                i += 1
                        return ''.join(result)
                    
                    code_content = preserve_spaces(code_content)
                    block_html = f'<pre style="{style_code_wrapper}"><code style="{style_code}">{code_content}</code></pre>'
                    html_lines.append(block_html)
                
                in_code_block = False
                code_block_content = []
                code_block_lang = ""
            else:
                # Start of code block
                in_code_block = True
                # Extract language
                code_block_lang = line.strip()[3:].strip().lower()
            continue
            
        if in_code_block:
            code_block_content.append(line)
            continue

        # Table detection
        if '|' in line and line.strip():
            flush_list()
            in_table = True
            table_lines.append(line)
            continue
        elif in_table:
            flush_table()

        # Horizontal rule
        if line.strip() == '---':
            flush_list()
            flush_table()
            html_lines.append(f'<hr style="{style_hr}">')
        
        # Headers
        elif line.startswith('# ') and not line.startswith('##'):
            flush_list()
            flush_table()
            html_lines.append(f'<h1 style="{style_h1}">{process_inline(line[2:])}</h1>')
        elif line.startswith('## ') and not line.startswith('###'):
            flush_list()
            flush_table()
            html_lines.append(f'<h2 style="{style_h2}">{process_inline(line[3:])}</h2>')
        elif line.startswith('### ') and not line.startswith('####'):
            flush_list()
            flush_table()
            html_lines.append(f'<h3 style="{style_h3}">{process_inline(line[4:])}</h3>')
        elif line.startswith('#### ') and not line.startswith('#####'):
            flush_list()
            flush_table()
            html_lines.append(f'<h4 style="{style_h4}">{process_inline(line[5:])}</h4>')
        elif line.startswith('##### ') and not line.startswith('######'):
            flush_list()
            flush_table()
            html_lines.append(f'<h5 style="{style_h5}">{process_inline(line[6:])}</h5>')
        elif line.startswith('###### '):
            flush_list()
            flush_table()
            html_lines.append(f'<h6 style="{style_h6}">{process_inline(line[7:])}</h6>')
        
        # Blockquotes
        elif line.startswith('> '):
            flush_list()
            flush_table()
            html_lines.append(f'<blockquote style="{style_blockquote}"><p style="{style_p}">{process_inline(line[2:])}</p></blockquote>')
            
        # Lists (Basic unordered)
        elif line.lstrip().startswith('- '): # Check lstrip() to catch indented lists
            flush_table()
            in_list = True
            # Calculate indent
            indent = get_indent(line)
            # Extract actual content
            content = line.strip()[2:] # remove '- '
            list_items.append((indent, process_inline(content)))
            
        # Paragraphs (skip empty lines)
        elif line.strip():
            if in_list and list_items:
                # Continuation of list item
                content = line.strip()
                # Update last item's content directly in the tuple? Tuples are immutable.
                # Reconstruct list item
                last_indent, last_content = list_items[-1]
                list_items[-1] = (last_indent, last_content + " " + process_inline(content))
            else:
                flush_list()
                flush_table()
                html_lines.append(f'<p style="{style_p}">{process_inline(line)}</p>')
        else:
            # Empty line - flush lists
            flush_list()
            flush_table()

    # Flush any remaining lists or tables
    flush_list()
    flush_table()

    full_content = '\n'.join(html_lines)
    
    # Wrap in container
    container_style = theme.get('container', '')
    article_style = theme.get('article', '')
    
    final_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
<div id="markdown-body">
  <div class="container-layout" style="{container_style}">
    <div class="article" style="{article_style}">
      {full_content}
    </div>
  </div>
</div>
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
  mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
</script>
</body>
</html>
"""
    return final_html

def main():
    args = parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file {args.input_file} does not exist.")
        sys.exit(1)
        
    theme = load_theme(args.theme)
    
    # Get the directory of the input file for resolving relative image paths
    input_file_dir = os.path.dirname(os.path.abspath(args.input_file))
    
    with open(args.input_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
        
    html_output = convert_markdown(md_content, theme, input_file_dir)
    
    output_filename = os.path.splitext(args.input_file)[0] + '.html'
    # Use utf-8-sig to include BOM, which helps some browsers/editors detect UTF-8 correctly for local files
    with open(output_filename, 'w', encoding='utf-8-sig') as f:
        f.write(html_output)
        
    print(f"Successfully converted {args.input_file} to {output_filename}")

if __name__ == '__main__':
    main()
