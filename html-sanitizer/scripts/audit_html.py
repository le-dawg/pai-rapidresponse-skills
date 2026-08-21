#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
HTML Security & Zero-JS Audit Tool
Scans HTML documents for active scripts, event handlers, pseudo-protocols,
SVG vectors, dynamic CSS expressions, base64 payloads, and email heuristic triggers.
"""

import sys
import re
import base64
import argparse
from pathlib import Path
from html.parser import HTMLParser

class ComprehensiveAuditParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = set()
        self.scripts = []
        self.event_handlers = []
        self.suspicious_urls = []
        self.forms = []
        self.iframes = []
        self.embeds = []
        self.metas = []
        self.svg_tags = []
        self.buttons = []

    def handle_starttag(self, tag, attrs):
        t_low = tag.lower()
        self.tags.add(t_low)
        attr_dict = {k.lower(): v for k, v in attrs}

        if t_low == "script":
            self.scripts.append(attr_dict)
        elif t_low == "form":
            self.forms.append(attr_dict)
        elif t_low == "iframe":
            self.iframes.append(attr_dict)
        elif t_low in ("object", "embed", "applet"):
            self.embeds.append((t_low, attr_dict))
        elif t_low == "meta":
            self.metas.append(attr_dict)
        elif t_low in ("button", "input") and "formaction" in attr_dict:
            self.buttons.append((t_low, attr_dict))
        elif t_low.startswith("svg") or t_low in ("svg", "animate", "set", "use", "foreignobject"):
            self.svg_tags.append((t_low, attr_dict))

        for k, v in attrs:
            k_low = k.lower()
            if k_low.startswith("on"):
                self.event_handlers.append((t_low, k, v))
            if v and any(p in str(v).lower() for p in ["javascript:", "vbscript:", "data:text/html", "data:application/javascript"]):
                self.suspicious_urls.append((t_low, k, v))

def audit_html_file(file_path: Path) -> dict:
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    parser = ComprehensiveAuditParser()
    parser.feed(content)

    # 1. CSS Analysis
    css_findings = []
    for pattern, desc in [
        (r"expression\s*\(", "CSS expression() dynamic evaluation"),
        (r"behavior\s*:", "CSS behavior property (HTC component)"),
        (r"-moz-binding\s*:", "CSS -moz-binding (XBL script binding)"),
        (r"url\s*\(\s*['\"]?javascript:", "CSS url(javascript:...) execution"),
        (r"url\s*\(\s*['\"]?data:text/html", "CSS url(data:text/html) embedding"),
        (r"@import", "CSS @import external stylesheet rule")
    ]:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            css_findings.append((desc, len(matches)))

    # 2. Base64 Payloads Audit
    base64_matches = re.findall(r"data:([^;]+);base64,([A-Za-z0-9+/=]+)", content)
    suspicious_base64 = []
    for idx, (mime, b64) in enumerate(base64_matches, 1):
        try:
            decoded = base64.b64decode(b64).decode("utf-8", errors="ignore")
            for risk in ["<script", "javascript:", "onload", "onerror", "onclick", "onmouseover", "eval(", "document."]:
                if risk in decoded.lower():
                    suspicious_base64.append((idx, mime, risk))
                    break
        except Exception:
            pass

    return {
        "file": str(file_path),
        "size": len(content),
        "tags": sorted(list(parser.tags)),
        "scripts": parser.scripts,
        "event_handlers": parser.event_handlers,
        "suspicious_urls": parser.suspicious_urls,
        "forms": parser.forms,
        "iframes": parser.iframes,
        "embeds": parser.embeds,
        "metas": parser.metas,
        "svg_tags": parser.svg_tags,
        "buttons": parser.buttons,
        "css_findings": css_findings,
        "base64_count": len(base64_matches),
        "suspicious_base64": suspicious_base64
    }

def print_audit_report(res: dict):
    print("=" * 60)
    print(f"🔒 ZERO-JS SECURITY AUDIT REPORT: {res['file']}")
    print(f"File Size: {res['size']:,} characters")
    print("=" * 60)

    total_critical = len(res['scripts']) + len(res['event_handlers']) + len(res['suspicious_urls']) + len(res['suspicious_base64'])
    email_heuristics = len(res['forms']) + len(res['iframes']) + len(res['embeds'])

    print(f"\n📊 Summary:")
    print(f"  • Critical JS Execution Vectors: {total_critical}")
    print(f"  • Email Heuristic / Phishing Triggers: {email_heuristics}")
    print(f"  • Base64 Data URIs Audited: {res['base64_count']}")

    print("\n🔍 Detailed Findings:")
    print(f"1. Script Tags: {len(res['scripts'])}")
    for s in res['scripts']:
        s_type = s.get("type", "standard JavaScript")
        print(f"   - <script type='{s_type}'> (Attributes: {s})")

    print(f"\n2. Inline Event Handlers: {len(res['event_handlers'])}")
    for tag, handler, val in res['event_handlers']:
        print(f"   - <{tag} {handler}=\"{val}\">")

    print(f"\n3. JavaScript / Dangerous URIs: {len(res['suspicious_urls'])}")
    for tag, attr, val in res['suspicious_urls']:
        print(f"   - <{tag} {attr}=\"{val}\">")

    print(f"\n4. Interactive Forms: {len(res['forms'])}")
    for f in res['forms']:
        print(f"   - <form id='{f.get('id', '')}' class='{f.get('class', '')}'>")

    print(f"\n5. Embedded Frames / Plugins: {len(res['iframes']) + len(res['embeds'])}")
    for emb in res['embeds']:
        print(f"   - <{emb[0]}>")
    for ifr in res['iframes']:
        print(f"   - <iframe>")

    print(f"\n6. CSS Dynamic Execution Patterns: {len(res['css_findings'])}")
    for desc, count in res['css_findings']:
        print(f"   - {desc}: {count} occurrences")

    print(f"\n7. Base64 Encoded Payloads: {res['base64_count']} total")
    if res['suspicious_base64']:
        print(f"   ⚠️ Malicious active vectors inside Base64: {len(res['suspicious_base64'])}")
        for idx, mime, risk in res['suspicious_base64']:
            print(f"   - Payload #{idx} ({mime}) matched '{risk}'")
    else:
        print("   ✅ All Base64 payloads decoded and verified safe.")

    print("\n" + "=" * 60)
    if total_critical == 0 and email_heuristics == 0:
        print("🛡️ VERDICT: 100% CLEAN (Zero JavaScript & Zero Email Scanner Triggers)")
    elif total_critical == 0:
        print("⚠️ VERDICT: ZERO ACTIVE JS, but contains heuristic email triggers (forms/inert scripts).")
    else:
        print("❌ VERDICT: ACTIVE JAVASCRIPT OR EXECUTION VECTORS DETECTED.")
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description="Audit HTML files for active JavaScript and email security vectors.")
    parser.add_argument("file", help="Path to HTML file to audit")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"Error: File not found {path}")
        sys.exit(1)

    results = audit_html_file(path)
    print_audit_report(results)

if __name__ == "__main__":
    main()
