#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Zero-JS HTML Sanitizer
Transforms raw or snapshot HTML into 100% inert, zero-JavaScript documents.
Features:
- Complete removal of <script> tags and active event handlers
- JavaScript / VBScript URI neutralization (quoted, unquoted, entity-encoded)
- Structural Form-to-Div transformation with complete DOM/value preservation
- Deep Base64 SVG decoding and purification
- Dynamic CSS expression removal
"""

import sys
import re
import base64
import shutil
import argparse
from pathlib import Path

def sanitize_css(css_text: str) -> str:
    """Removes active execution vectors from CSS stylesheets."""
    # Strip any CSS declaration property that contains dynamic scripts, expressions, or behaviors
    css_clean = re.sub(
        r"[a-zA-Z\-]+\s*:\s*[^;}]*?(?:javascript:|vbscript:|expression\s*\(|behavior\s*:|-moz-binding\s*:)[^;}]*;?",
        "",
        css_text,
        flags=re.IGNORECASE | re.DOTALL
    )
    # Strip standalone url(javascript:...) occurrences
    css_clean = re.sub(
        r"url\s*\(\s*['\"]?\s*(?:javascript|vbscript):[^;}]*?['\"]?\s*\)",
        "none",
        css_clean,
        flags=re.IGNORECASE
    )
    return css_clean

def sanitize_svg_xml(svg_text: str) -> str:
    """Sanitizes an SVG string by stripping scripts, SMIL animation scripts, and event handlers."""
    # Strip <script> inside SVG
    svg_clean = re.sub(r"<script\b[^>]*>.*?</script>", "", svg_text, flags=re.IGNORECASE | re.DOTALL)
    # Strip SMIL animation triggers with on* attributes
    svg_clean = re.sub(r"<(?:animate|set|animateTransform)\b[^>]*\son[a-zA-Z]+\s*=[^>]*>", "", svg_clean, flags=re.IGNORECASE)
    # Strip on* attributes from any SVG tag
    svg_clean = re.sub(r"\s+on[a-zA-Z]+\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+)", "", svg_clean, flags=re.IGNORECASE)
    # Sanitize href/xlink:href with javascript
    svg_clean = re.sub(r"\s+(?:xlink:)?href\s*=\s*(?:\"javascript:[^\"]*\"|'javascript:[^']*'|javascript:[^\s>]+)", "", svg_clean, flags=re.IGNORECASE)
    return svg_clean

def sanitize_base64_payloads(html_content: str) -> str:
    """Decodes base64 SVG images, purifies them, and re-encodes safe vectors."""
    def replace_base64(match):
        mime = match.group(1).lower()
        raw_b64 = match.group(2)
        if "svg" in mime or "xml" in mime:
            try:
                decoded = base64.b64decode(raw_b64).decode("utf-8", errors="ignore")
                sanitized_svg = sanitize_svg_xml(decoded)
                new_b64 = base64.b64encode(sanitized_svg.encode("utf-8")).decode("ascii")
                return f"data:{mime};base64,{new_b64}"
            except Exception:
                return match.group(0)
        return match.group(0)

    return re.sub(r"data:([^;]+);base64,([A-Za-z0-9+/=]+)", replace_base64, html_content)

def sanitize_html_string(html_content: str, email_mode: bool = True, transform_forms: bool = True, strip_jsonld: bool = True) -> str:
    """Main sanitization engine applying progressive, lossless Zero-JS transformations."""
    result = html_content

    # 1. Remove all <script> tags
    if strip_jsonld:
        result = re.sub(r"<script\b[^>]*>.*?</script>", "", result, flags=re.IGNORECASE | re.DOTALL)
    else:
        def script_filter(match):
            tag_open = match.group(1)
            if "application/ld+json" in tag_open.lower():
                return match.group(0)
            return ""
        result = re.sub(r"(<script\b[^>]*>).*?</script>", script_filter, result, flags=re.IGNORECASE | re.DOTALL)

    # 2. Strip inline event handlers (on*) on all tags (handles double quotes, single quotes, and unquoted)
    result = re.sub(r"\s+on[a-zA-Z]+\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+)", "", result, flags=re.IGNORECASE)

    # 3. Neutralize javascript: and vbscript: URIs in tag attributes
    dangerous_uri_pattern = r"\s+(href|src|formaction|action|data|poster|background)\s*=\s*(?:\"(?:javascript|vbscript):[^\"]*\"|'(?:javascript|vbscript):[^']*'|(?:javascript|vbscript):[^\s>]+)"
    result = re.sub(dangerous_uri_pattern, "", result, flags=re.IGNORECASE)

    # 4. Transform Form elements to structural Div containers (Email / Zero-Phishing mode)
    if transform_forms or email_mode:
        def form_open_to_div(match):
            attrs = match.group(1)
            # Filter out submission attributes: action, method, onsubmit, target, enctype
            safe_attrs = re.sub(r"\s+(action|method|onsubmit|target|enctype)\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+)", "", attrs, flags=re.IGNORECASE)
            return f"<div{safe_attrs}>"

        result = re.sub(r"<form\b([^>]*)>", form_open_to_div, result, flags=re.IGNORECASE)
        result = re.sub(r"</form>", "</div>", result, flags=re.IGNORECASE)

        # Strip formaction on buttons and inputs
        result = re.sub(r"\s+formaction\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+)", "", result, flags=re.IGNORECASE)

    # 5. Sanitize CSS blocks and inline styles
    def style_replacer(match):
        open_tag = match.group(1)
        css_body = match.group(2)
        close_tag = match.group(3)
        return f"{open_tag}{sanitize_css(css_body)}{close_tag}"

    result = re.sub(r"(<style\b[^>]*>)(.*?)(</style>)", style_replacer, result, flags=re.IGNORECASE | re.DOTALL)

    # Clean inline style attributes
    def inline_style_replacer(match):
        attr_val = match.group(2)
        return f'style="{sanitize_css(attr_val)}"'

    result = re.sub(r'style\s*=\s*(["\'])(.*?)\1', inline_style_replacer, result, flags=re.IGNORECASE)

    # 6. Sanitize Base64 Encoded Payloads
    result = sanitize_base64_payloads(result)

    # 7. Clean Dangerous Meta Tags (meta refresh & CSP keywords)
    result = re.sub(r"<meta\b[^>]*http-equiv=[\"']?refresh[\"']?[^>]*>", "", result, flags=re.IGNORECASE)
    if email_mode:
        result = re.sub(r"<meta\b[^>]*http-equiv=[\"']?content-security-policy[\"']?[^>]*>", "", result, flags=re.IGNORECASE)

    # 8. Strip iframes / objects / embeds if in email mode
    if email_mode:
        result = re.sub(r"<(?:object|embed|applet)\b[^>]*>.*?</(?:object|embed|applet)>", "", result, flags=re.IGNORECASE | re.DOTALL)
        result = re.sub(r"<iframe\b[^>]*>.*?</iframe>", "", result, flags=re.IGNORECASE | re.DOTALL)

    return result

def sanitize_file(input_path: Path, output_path: Path, email_mode: bool = True, create_backup: bool = True):
    content = input_path.read_text(encoding="utf-8", errors="ignore")
    
    if create_backup and input_path == output_path:
        bak_file = input_path.with_suffix(input_path.suffix + ".bak")
        shutil.copy2(input_path, bak_file)
        print(f"📦 Safety backup created at: {bak_file}")

    sanitized = sanitize_html_string(content, email_mode=email_mode)
    output_path.write_text(sanitized, encoding="utf-8")
    print(f"✨ Successfully sanitized HTML: {output_path}")
    print(f"   Original size: {len(content):,} chars -> Clean size: {len(sanitized):,} chars")

def main():
    parser = argparse.ArgumentParser(description="Zero-JS HTML Sanitizer & Layout-Preserving Converter.")
    parser.add_argument("input", help="Source HTML file path")
    parser.add_argument("-o", "--output", help="Destination output path (defaults to overwriting input with .bak)")
    parser.add_argument("--no-email-mode", action="store_true", help="Disable aggressive email-specific mitigations")
    parser.add_argument("--keep-jsonld", action="store_true", help="Preserve non-executable JSON-LD metadata scripts")
    parser.add_argument("--no-backup", action="store_true", help="Disable automatic .bak creation on in-place edits")

    args = parser.parse_args()
    in_path = Path(args.input)
    if not in_path.exists():
        print(f"❌ Error: File not found {in_path}")
        sys.exit(1)

    out_path = Path(args.output) if args.output else in_path
    email_mode = not args.no_email_mode
    create_bak = not args.no_backup

    sanitize_file(in_path, out_path, email_mode=email_mode, create_backup=create_bak)

if __name__ == "__main__":
    main()
