---
name: html-sanitizer
description: >-
  Use when auditing, cleaning, or converting HTML files, single-page web archives (SingleFile/Monolith), email templates, or rich-text snippets. Trigger on slash commands: /sanitize-html, /sanitize, /audit-html, /zero-js.
---

# HTML Sanitizer & Zero-JS Converter

## Overview
This skill provides deterministic methodologies, threat matrices, and automated CLI tools to audit, sanitize, and convert HTML documents into **100% inert, zero-JavaScript assets**. It guarantees complete elimination of active code execution vectors while preserving visual layouts, CSS styling, typography, and pre-filled form values (textareas, inputs, and checkboxes).

---

## Slash Commands & Triggers

- **`/sanitize [file]`** or **`/sanitize-html [file]`**: Performs full Zero-JS sanitization, converts `<form>` to `<div>`, and purifies Base64 SVG and CSS assets with automatic `.bak` safety backup.
- **`/audit-html [file]`**: Runs an exhaustive 10-vector security audit and prints a zero-JS compliance report.
- **`/zero-js [file]`**: Synonym for full sanitization and form flattening.

## When to Use

- **Email Client Pre-flight**: Preparing single-page HTML snapshots or newsletters for Thunderbird, Outlook, Apple Mail, or Gmail without triggering security banners or anti-spam heuristic filters (`HTML_SCRIPT_TAG`, `HTML_FORM_ACTION`).
- **Static Web Archives**: Converting interactive SingleFile, Monolith, or DOM snapshots into permanent, immutable visual archives.
- **Form Flattening**: Converting interactive `<form>` elements into structural `<div>` containers while preserving all child inputs, filled-out text, formulas, IDs, and CSS classes.
- **Vector & Asset Purification**: Auditing and cleaning embedded SVG vectors, Base64 data URIs (`data:image/svg+xml;base64`), and dynamic CSS expressions.

## When NOT to Use

- When preserving active client-side JavaScript interactivity (e.g. dynamic Vue/React single-page applications) is required.
- Simple markdown-only text formatting tasks.

---

## Zero-JS Execution Vectors Matrix

| Vector Category | Specific Threats | Sanitization Strategy |
| :--- | :--- | :--- |
| **Direct Scripts** | `<script>`, `<script src="...">`, `<script type="module">` | Unconditionally strip all `<script>` tags. |
| **Inert Metadata Scripts** | `<script type="application/ld+json">`, `<template>` | Strip in email contexts to prevent naive regex scanner alerts. |
| **Inline Event Handlers** | `onload`, `onclick`, `onerror`, `onmouseover`, `ontoggle`, etc. | Strip all attributes matching `^on[a-zA-Z]+`. |
| **Dangerous URIs** | `javascript:`, `vbscript:`, unsafe `data:` URLs in `href`, `src`, `formaction` | Strip attribute or replace with safe link. |
| **SVG Active Content** | Embedded `<script>`, SMIL `<animate onbegin="...">`, `xlink:href="javascript:..."` | Recursively strip scripts and event triggers in SVG markup. |
| **Base64 Payloads** | Encoded SVG vectors (`data:image/svg+xml;base64,...`) | Decode Base64, purify XML tree, and re-encode safe output. |
| **CSS Dynamic Vectors** | `expression(...)`, `-moz-binding`, `behavior:`, `url(javascript:...)` | Strip dynamic declarations from `<style>` and `style=""` attributes. |
| **Interactive Forms** | `<form action="..." method="...">`, `<button formaction="...">` | Convert `<form>` to `<div>`; drop `action`/`method`; retain classes/values. |
| **Meta Directives** | `<meta http-equiv="refresh">`, CSP misconfigurations | Remove meta refresh and unneeded CSP tags. |

*For deep dive on all 40+ vectors, see [references/vector_matrix.md](references/vector_matrix.md).*

---

## Core Execution Runbook

### Step 1: Pre-Sanitization Security Audit
Scan the target HTML document to identify active code execution vectors, form tags, and embedded Base64 payloads:
```bash
uv run scripts/audit_html.py <path-to-html>
```

### Step 2: Zero-JS Sanitization & Form Flattening
Sanitize the document using the bundled deterministic tool:
```bash
# In-place sanitization with automatic safety backup (.bak)
uv run scripts/sanitize_html.py <path-to-html>

# Or output to a dedicated destination file:
uv run scripts/sanitize_html.py <input.html> -o <sanitized.html>
```

### Step 3: Post-Sanitization Verification
Re-run the security audit to guarantee 0 active vectors and 0 heuristic warnings:
```bash
uv run scripts/audit_html.py <path-to-sanitized-html>
```

---

## Form-to-Div Transformation Standard

To prevent email client security warnings while preserving visual presentation and user-entered content:
1. **Container Transformation**: Replace `<form id="x" class="y project-form" style="...">` with `<div id="x" class="y project-form" style="...">`.
2. **Close Tag Transformation**: Replace `</form>` with `</div>`.
3. **Attribute Stripping**: Drop `action`, `method`, `onsubmit`, `target`, `enctype`.
4. **Data Preservation**: Retain all child `<input>`, `<textarea>`, `<select>`, `<label>`, and formatting containers. Ensure filled values (in `value="..."` attributes and `<textarea>` text bodies) remain intact.
5. **Button Neutralization**: Strip `formaction` attributes from child `<button>` and `<input>` elements.

---

## Common Pitfalls & Rationalizations

| Pitfall / Rationalization | Why It Fails | Correct Mitigation |
| :--- | :--- | :--- |
| *"JSON-LD `<script>` is just metadata, so it's safe to keep in emails."* | Email antimalware engines (e.g. SpamAssassin) often use naive regexes (`<script`) that flag the message as suspicious. | Strip JSON-LD `<script>` tags when targeting email delivery. |
| *"Replacing `<form>` with `<div>` will break form styles."* | Most stylesheets use classes (`.project-form`) or IDs (`#input_0`), not bare `form` tags. | Migrate all classes, IDs, styles, and data attributes to the replacement `<div>`. |
| *"Regex matching `href="javascript:..."` is enough."* | Javascript URLs can contain spaces, single/double quotes, and parentheses (e.g. `href="javascript:alert('X')"`). | Match quoted, unquoted, and nested-string attribute boundaries properly. |
| *"Base64 images are just images."* | SVGs encoded in `data:image/svg+xml;base64` can contain fully functional `<script>` and SMIL triggers. | Deep-decode and sanitize all Base64 SVG payloads. |

---

## Verification Checklist

- [ ] Security audit reports `0` `<script>` tags.
- [ ] Security audit reports `0` inline event handlers (`on*`).
- [ ] Security audit reports `0` `javascript:` / `vbscript:` URIs.
- [ ] All `<form>` containers safely converted to `<div ...>` with original classes/IDs.
- [ ] All pre-filled textareas and input values verified intact.
- [ ] Embedded Base64 SVGs decoded and verified clean.
- [ ] CSS stylesheets verified free of `expression()`, `-moz-binding`, and `behavior`.
- [ ] Document verified in browser / email viewer without layout shift or styling degradation.
