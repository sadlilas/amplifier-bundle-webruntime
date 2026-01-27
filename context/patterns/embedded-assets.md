# Embedded Assets Pattern

Browser Amplifier applications require two embedded assets to run offline:

1. **amplifier-core wheel** - The Python package (base64 encoded)
2. **amplifier-browser.py module** - The browser runtime bridge (base64 encoded)

## Why Embed Assets?

- **Single-file distribution** - One HTML file contains everything
- **Offline capability** - Works without network after initial load
- **No CORS issues** - Assets are same-origin
- **Portability** - Share via email, USB, etc.

## Asset Structure

```html
<!-- Embedded amplifier-core wheel -->
<script id="amplifier-wheel-b64" type="text/plain">
UEsDBBQAAAAIANlYd1oAAA...  <!-- base64 encoded .whl file -->
</script>

<!-- Embedded amplifier-browser.py module -->
<script id="amplifier-browser-py" type="text/plain">
IyBhbXBsaWZpZXItYnJvd3...  <!-- base64 encoded Python code -->
</script>
```

## Extracting Assets from a Working Example

The canonical source for these assets is `amplifier-in-action.html` in the webllm-bundle workspace.

### Manual Extraction

```javascript
// In browser console on a working example:
const wheel = document.getElementById('amplifier-wheel-b64').textContent;
const module = document.getElementById('amplifier-browser-py').textContent;
console.log('Wheel length:', wheel.length);
console.log('Module length:', module.length);
```

### Programmatic Extraction (Python)

```python
import re

with open('amplifier-in-action.html', 'r') as f:
    content = f.read()

# Extract wheel
wheel_match = re.search(
    r'<script id="amplifier-wheel-b64" type="text/plain">(.*?)</script>',
    content, re.DOTALL
)
wheel_b64 = wheel_match.group(1).strip() if wheel_match else None

# Extract module
module_match = re.search(
    r'<script id="amplifier-browser-py" type="text/plain">(.*?)</script>',
    content, re.DOTALL
)
module_b64 = module_match.group(1).strip() if module_match else None
```

### Programmatic Extraction (JavaScript/Node)

```javascript
const fs = require('fs');
const content = fs.readFileSync('amplifier-in-action.html', 'utf8');

const wheelMatch = content.match(/<script id="amplifier-wheel-b64" type="text\/plain">([\s\S]*?)<\/script>/);
const moduleMatch = content.match(/<script id="amplifier-browser-py" type="text\/plain">([\s\S]*?)<\/script>/);

const wheelB64 = wheelMatch ? wheelMatch[1].trim() : null;
const moduleB64 = moduleMatch ? moduleMatch[1].trim() : null;
```

## Using Embedded Assets

### Installing the Wheel

```javascript
// Get the base64 content
const wheelB64 = document.getElementById('amplifier-wheel-b64').textContent.trim();

// Decode to bytes
const wheelBytes = Uint8Array.from(atob(wheelB64), c => c.charCodeAt(0));

// Write to Pyodide filesystem
pyodide.FS.writeFile('/tmp/amplifier_core-1.0.0-py3-none-any.whl', wheelBytes);

// Install with micropip
await micropip.install('emfs:/tmp/amplifier_core-1.0.0-py3-none-any.whl');
```

### Loading the Browser Module

```javascript
// Get and decode the module
const moduleB64 = document.getElementById('amplifier-browser-py').textContent.trim();
const moduleCode = atob(moduleB64);

// Execute in Pyodide
await pyodide.runPythonAsync(moduleCode);

// Now you have access to create_session()
```

## Creating New Embedded Assets

### Building amplifier-core Wheel

```bash
cd amplifier-core
uv build
# Output: dist/amplifier_core-1.0.0-py3-none-any.whl
```

### Encoding to Base64

```bash
# Encode wheel
base64 -w 0 dist/amplifier_core-1.0.0-py3-none-any.whl > wheel.b64

# Encode Python module
base64 -w 0 amplifier_browser.py > module.b64
```

### Python Alternative

```python
import base64

# Encode wheel
with open('amplifier_core-1.0.0-py3-none-any.whl', 'rb') as f:
    wheel_b64 = base64.b64encode(f.read()).decode('ascii')

# Encode module
with open('amplifier_browser.py', 'r') as f:
    module_b64 = base64.b64encode(f.read().encode('utf-8')).decode('ascii')
```

## Asset Sizes (Approximate)

| Asset | Raw Size | Base64 Size |
|-------|----------|-------------|
| amplifier-core wheel | ~150 KB | ~200 KB |
| amplifier-browser.py | ~8 KB | ~11 KB |
| **Total** | ~158 KB | ~211 KB |

## Best Practices

1. **Always extract from a working example** - Don't try to build from scratch
2. **Verify assets load** - Test wheel installation before adding UI
3. **Keep assets updated** - When amplifier-core updates, re-extract
4. **Compress if needed** - For very large apps, consider gzip + base64

## Troubleshooting

### "Module not found" after install

The wheel may be corrupted. Re-extract from a working example.

### Base64 decode errors

Check for whitespace/newlines in the base64 content. Use `.trim()` before decoding.

### Pyodide FS errors

Ensure the `/tmp/` directory exists (it should by default in Pyodide).
