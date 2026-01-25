# amplifier-bundle-browser

Browser runtime for Amplifier - run AI agents entirely in web browsers.

## Overview

This bundle enables running Amplifier applications in web browsers using:

- **Pyodide** - Python interpreter compiled to WebAssembly
- **amplifier-core** - The Amplifier kernel running in Pyodide
- **Browser-specific tools** - Storage, fetch, and other browser APIs

**Provider-agnostic**: This bundle provides the runtime infrastructure. Compose it with your choice of provider:

- [amplifier-bundle-webllm](https://github.com/microsoft/amplifier-bundle-webllm) - Local inference via WebGPU
- OpenAI/Anthropic - Cloud APIs (user provides key)

## Quick Start

### 1. Compose Your Bundle

```yaml
# my-browser-app.yaml
includes:
  - bundle: git+https://github.com/microsoft/amplifier-bundle-browser@main
  - bundle: git+https://github.com/microsoft/amplifier-bundle-webllm@main  # or your provider
```

### 2. Set Up HTML

```html
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js"></script>
    <script type="module">
        import { CreateMLCEngine } from 'https://esm.run/@mlc-ai/web-llm';
        
        // Initialize Pyodide + Amplifier
        const pyodide = await loadPyodide();
        await pyodide.loadPackage('micropip');
        await pyodide.runPythonAsync(`
            import micropip
            await micropip.install('amplifier-core')
        `);
        
        // Initialize WebLLM (or your provider)
        const engine = await CreateMLCEngine('Phi-3.5-mini-instruct-q4f16_1-MLC');
        
        // Set up bridge and start session
        // (See full examples in docs/)
    </script>
</head>
<body>
    <div id="chat"></div>
</body>
</html>
```

## What's Included

### Tools

| Tool | Description |
|------|-------------|
| `tool-browser-storage` | localStorage/IndexedDB access |
| `tool-todo` | Task tracking (in-memory) |

### Agents

| Agent | Description |
|-------|-------------|
| `browser-developer` | Expert for building browser Amplifier integrations |

### Context

- `browser-guide.md` - Browser capabilities, constraints, and patterns

## Directory Structure

```
amplifier-bundle-browser/
├── bundle.yaml                 # Main entry point
├── behaviors/
│   └── browser-runtime.yaml    # Core browser behavior
├── agents/
│   └── browser-developer.md    # Integration expert
├── context/
│   └── browser-guide.md        # Browser-specific guidance
└── modules/
    └── tool-browser-storage/   # Browser storage tool
```

## Browser Requirements

| Browser | Support |
|---------|---------|
| Chrome 113+ | ✅ Full (WebGPU for local inference) |
| Edge 113+ | ✅ Full |
| Safari 18+ | ✅ Full |
| Firefox | ⚠️ WebGPU behind flag |

## Constraints vs Desktop Amplifier

| Feature | Desktop | Browser |
|---------|---------|---------|
| Filesystem access | ✅ Full | ❌ None |
| Shell commands | ✅ Full | ❌ None |
| Persistent storage | ✅ Files | ⚠️ localStorage/IndexedDB |
| Memory | ✅ System RAM | ⚠️ Tab limit (~2-4GB) |
| Network | ✅ Full | ⚠️ CORS restrictions |

## Composition Examples

### With WebLLM (Local Inference)

```yaml
includes:
  - bundle: git+https://github.com/microsoft/amplifier-bundle-browser@main
  - bundle: git+https://github.com/microsoft/amplifier-bundle-webllm@main
```

### With OpenAI (Cloud API)

```yaml
includes:
  - bundle: git+https://github.com/microsoft/amplifier-bundle-browser@main

providers:
  - module: provider-openai
    source: git+https://github.com/microsoft/amplifier-module-provider-openai@main
    config:
      api_key: ${OPENAI_API_KEY}  # User provides at runtime
```

## Development

### Using the browser-developer Agent

The `browser-developer` agent can help you build browser Amplifier integrations:

```
"Help me create a browser chat interface with WebLLM"
"Debug why my browser Amplifier app isn't loading"
"Show me how to add persistent storage to my browser app"
```

### Testing Locally

```bash
# Serve the examples directory
cd examples
python -m http.server 8080

# Open http://localhost:8080 in browser
```

## License

MIT

## Related

- [amplifier-bundle-webllm](https://github.com/microsoft/amplifier-bundle-webllm) - WebLLM provider
- [amplifier-core](https://github.com/microsoft/amplifier-core) - Amplifier kernel
- [Pyodide](https://pyodide.org/) - Python in WebAssembly
- [WebLLM](https://webllm.mlc.ai/) - Browser-based LLM inference
