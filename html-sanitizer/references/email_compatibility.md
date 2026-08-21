# Email Client Compatibility & Security Scanner Guidelines

Email clients utilize specialized rendering engines and aggressive heuristic security filters to protect users from malicious payloads, tracking beacons, and phishing forms.

---

## 1. Major Email Rendering Engines

| Client Category | Primary Engines | Scripting Behavior | Form Support | CSS Constraints |
| :--- | :--- | :--- | :--- | :--- |
| **Microsoft Outlook (Desktop Windows)** | Microsoft Word (`winword.exe`) / Trident | Scripts stripped entirely; `<script>` tags trigger security banners. | Forms disabled or broken visually. | No modern CSS Grid/Flexbox; requires table-based layouts or inline styles. |
| **Microsoft Outlook (Mac / Web / New)** | WebKit / Blink | Scripts stripped. | Forms trigger phishing/security warnings. | Full CSS support with standard web rendering. |
| **Mozilla Thunderbird** | Gecko Engine | JavaScript disabled by default in email views (`javascript.allow.mailnews = false`). `<script>` blocks generate security warnings. | Forms disabled; clicking submit triggers browser warning or is blocked. | Full modern CSS support; identical to Firefox layout engine. |
| **Apple Mail (macOS / iOS)** | WebKit | Scripts stripped before rendering. | Forms rendered, but submission often suppressed or routed to Safari. | Exceptional CSS support (media queries, flexbox, SVG). |
| **Gmail (Web & Mobile)** | Blink (pre-sanitized by Google Caja / internal sanitizer) | Strips all `<script>`, `<form>`, `<style>` expression properties, and arbitrary attributes. | `<form>` elements stripped into non-functional plain markup. | Inlines styles; strips external stylesheets unless in `<style>` block in `<head>`. |

---

## 2. Anti-Spam & Heuristic Scanner Triggers

Security gateways (e.g., SpamAssassin, Microsoft Defender for Office 365, Proofpoint, Cisco IronPort) analyze raw MIME bodies:

1. **Literal `<script>` Strings**:
   * *Rule*: Even if a script is inert (e.g., `<script type="application/ld+json">`), rule-based filters (like `HTML_SCRIPT_TAG`) increment the spam score because legitimate HTML emails rarely require schema scripts.
   * *Mitigation*: Strip all `<script>` tags regardless of `type`.
2. **Interactive `<form>` Elements**:
   * *Rule*: Forms are high-risk indicators of credential harvesting and phishing attacks (`HTML_FORM_ACTION`).
   * *Mitigation*: Transform `<form>` tags into `<div>` tags, retaining IDs and CSS classes so visual layout remains identical.
3. **Data Protocol Exploits**:
   * *Rule*: Base64 data URIs containing HTML or XML payloads are often inspected for evasion techniques.
   * *Mitigation*: Purify all base64-encoded SVG images to ensure 0 `<script>` or event handler tags exist in the decoded stream.
4. **Content Security Policy Tags**:
   * *Rule*: `<meta http-equiv="content-security-policy" ...>` containing strings like `script-src 'unsafe-inline'` can trigger regex-based alert filters looking for keyword anomalies.
   * *Mitigation*: Remove CSP meta tags in emails, as email engines ignore client CSP headers anyway.
