# 🛡️ HTML Sanitizer & Zero-JS Converter

[![AgentSkills.io Standard](https://img.shields.io/badge/AgentSkills.io-Compatible-00D084?style=flat-square)](https://agentskills.io)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)](https://python.org)
[![Fast uv Powered](https://img.shields.io/badge/Powered%20By-uv-8A2BE2?style=flat-square)](https://github.com/astral-sh/uv)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

A production-grade AI agent skill and standalone CLI toolkit for **auditing, sanitizing, and flattening HTML documents into 100% inert, zero-JavaScript assets**.

Designed specifically for **email client pre-flight**, **static web snapshots (SingleFile/Monolith)**, and **anti-phishing form flattening** without sacrificing visual typography, layouts, or pre-filled form values.

---

## 🚀 Key Features

* **Zero-JavaScript Guarantee**: Completely purges `<script>` tags, inline event handlers (`onload`, `onclick`, `onerror`, `ontoggle`), and dangerous `javascript:`/`vbscript:` protocol schemes.
* **Lossless Form-to-Div Transformation**: Converts interactive `<form>` tags into styled `<div>` containers, neutralizes submit actions, and preserves 100% of user-entered text, formulas, checkboxes, IDs, and CSS classes.
* **Deep Base64 SVG Purification**: Decodes embedded `data:image/svg+xml;base64` payloads, strips internal script tags and SMIL animation triggers (`<animate onbegin="...">`), and safely re-encodes clean assets.
* **Dynamic CSS Neutralization**: Removes legacy and browser-specific dynamic execution vectors (`expression()`, `-moz-binding`, `behavior:`, `url(javascript:...)`).
* **Multi-Harness Ready**: Compatible with **Google Antigravity (AGY)**, **Claude Code**, **OpenCode**, **Goose**, and the **AgentSkills.io** standard.

---

## 📦 Installation & Harness Setup

### 1. Antigravity / AGY
Install globally:
```bash
cp -r html-sanitizer ~/.gemini/config/skills/
```
Or project-locally:
```bash
cp -r html-sanitizer .agents/skills/
```

### 2. Claude Code
Install project-locally:
```bash
mkdir -p .claude/skills && cp -r html-sanitizer .claude/skills/
```

### 3. Goose / OpenCode
Install into Goose:
```bash
mkdir -p ~/.config/goose/skills && cp -r html-sanitizer ~/.config/goose/skills/
```

---

## ⚡ CLI Usage

All tools run deterministically using [`uv`](https://github.com/astral-sh/uv):

### 1. Security Audit (10-Vector Scan)
```bash
uv run html-sanitizer/scripts/audit_html.py path/to/document.html
```

**Sample Output:**
```text
============================================================
🔒 ZERO-JS SECURITY AUDIT REPORT: document.html
File Size: 1,102,387 characters
============================================================
📊 Summary:
  • Critical JS Execution Vectors: 0
  • Email Heuristic / Phishing Triggers: 0
  • Base64 Data URIs Audited: 25 (All Clean)
🛡️ VERDICT: 100% CLEAN (Zero JavaScript & Zero Email Scanner Triggers)
============================================================
```

### 2. Lossless Sanitization & Form Flattening
```bash
# In-place with automatic .bak safety backup
uv run html-sanitizer/scripts/sanitize_html.py path/to/document.html

# Output to a specific file
uv run html-sanitizer/scripts/sanitize_html.py dirty.html -o clean.html
```

---

## 🤖 Agent Slash Commands

When interacting with an AI coding agent with this skill loaded:

| Command | Action |
| :--- | :--- |
| **`/sanitize [file]`** | Sanitizes target HTML to zero-JS and flattens forms |
| **`/audit-html [file]`** | Scans file for all 10 JS execution vectors |
| **`/zero-js [file]`** | Flatten forms and strip all active scripts |

---

## 📚 Technical References

- [Vector Threat Matrix](references/vector_matrix.md): Exhaustive analysis of 40+ JavaScript execution vectors.
- [Email Compatibility Guide](references/email_compatibility.md): Engine behavior across Gecko (Thunderbird), WebKit (Apple Mail), Word/Trident (Outlook), and Blink (Gmail).

---

## 📄 License
MIT License. Part of the [`pai-rapidresponse-skills`](https://github.com/le-dawg/pai-rapidresponse-skills) collection.
