# Browser Amplifier Guide

This document provides context for AI assistants working with browser-based Amplifier applications.

---

## IMPORTANT: Purpose of This Bundle

**This bundle is for building Amplifier applications that run in browsers using Pyodide.**

It is **NOT** for:
- Raw JavaScript WebLLM apps
- Pure JS chat interfaces without Amplifier
- Standalone LLM demos that bypass Amplifier

### The Default Architecture

When someone asks for "WebLLM in browser", "browser AI", or "local LLM chat", the answer is:

```
Amplifier + Pyodide + WebLLM provider
```

**NOT** raw JavaScript calling WebLLM directly.

### Why Amplifier in Browser?

Using Amplifier (via Pyodide) instead of raw JavaScript provides:
- **Session management** - Conversation history, context handling
- **Tool system** - Browser-storage, todo, and custom tools
- **Provider abstraction** - Switch between WebLLM, OpenAI, Anthropic seamlessly
- **Hooks** - Logging, approval gates, observability
- **Consistency** - Same Amplifier patterns work in CLI and browser

Raw JavaScript WebLLM is fine for demos, but **real applications should use Amplifier**.

---

## What is Browser Amplifier?

Browser Amplifier runs the full Amplifier stack (amplifier-core, tools, providers) inside a web browser using:

- **Pyodide**: Python interpreter compiled to WebAssembly
- **amplifier-core**: The Amplifier kernel running in Pyodide
- **Provider bridge**: JavaScript↔Python communication for LLM calls

This enables:
- Fully client-side AI applications
- Offline-capable AI (with WebLLM)
- No server infrastructure required
- User data stays in browser

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  User's Browser                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐      ┌─────────────────────────────┐  │
│  │  Your Web App   │      │  LLM Provider               │  │
│  │  (HTML/JS/CSS)  │      │  ┌─────────────────────┐    │  │
│  └────────┬────────┘      │  │ WebLLM (local GPU)  │    │  │
│           │               │  ├─────────────────────┤    │  │
│           ▼               │  │ OpenAI API (fetch)  │    │  │
│  ┌─────────────────┐      │  ├─────────────────────┤    │  │
│  │  Pyodide        │◄────►│  │ Anthropic API       │    │  │
│  │  (Python WASM)  │      │  └─────────────────────┘    │  │
│  │                 │      └─────────────────────────────┘  │
│  │  ┌───────────┐  │                                       │
│  │  │ amplifier │  │      ┌─────────────────────────────┐  │
│  │  │   -core   │  │      │  Browser Storage            │  │
│  │  └───────────┘  │      │  ├── localStorage           │  │
│  └─────────────────┘      │  └── IndexedDB              │  │
│                           └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Available Tools

### tool-browser-storage

Browser-specific storage tool using localStorage and IndexedDB.

**Operations:**
- `storage_get(key)` - Retrieve a value
- `storage_set(key, value)` - Store a value
- `storage_delete(key)` - Remove a value
- `storage_list()` - List all keys
- `storage_clear()` - Clear all storage

**Limits:**
- localStorage: ~5-10MB per origin
- IndexedDB: Much larger (browser-dependent)

### tool-todo

Standard todo tool works in browser (in-memory state).

### NOT Available in Browser

- `tool-filesystem` - No filesystem access
- `tool-bash` - No shell access
- `tool-search` (grep/glob) - No filesystem to search

---

## Provider Options

### Local Inference (WebLLM)

Runs LLMs directly in browser using WebGPU.

**Requirements:**
- WebGPU-capable browser (Chrome 113+, Edge 113+)
- Sufficient VRAM (4GB+ for small models)
- Initial model download (2-8GB depending on model)

**Pros:**
- Fully offline after initial download
- Complete privacy (data never leaves device)
- No API costs

**Cons:**
- Requires modern GPU
- Large initial download
- Limited model selection

### API Providers (OpenAI, Anthropic)

Calls cloud APIs via browser fetch.

**Requirements:**
- User provides API key
- Network connectivity
- CORS-compatible endpoints

**Pros:**
- Powerful models (GPT-4, Claude)
- No local hardware requirements
- Fast responses

**Cons:**
- Requires API key (user must provide)
- Costs money per request
- Requires network

---

## Browser Constraints

### No Filesystem

Browser has no access to local filesystem. Use:
- `tool-browser-storage` for persistent data
- In-memory state for session data
- User file picker for explicit file access

### CORS Restrictions

Browser enforces Cross-Origin Resource Sharing:
- API calls must go to CORS-enabled endpoints
- OpenAI and Anthropic APIs support CORS
- Custom backends need CORS headers

### Memory Limits

Browser tabs have limited memory:
- Typical limit: 2-4GB per tab
- WebLLM models consume significant memory
- Context window size affects memory usage

### Storage Quotas

Browser storage has limits:
- localStorage: ~5-10MB
- IndexedDB: Larger but browser-dependent
- Can be cleared by user or browser

### Content Security Policy

Some sites restrict JavaScript execution:
- May block inline scripts
- May block external script sources
- May block eval() (affects some libraries)

---

## Initialization Patterns

### Basic Initialization

```javascript
async function initAmplifier() {
    // 1. Load Pyodide
    const pyodide = await loadPyodide();
    
    // 2. Install packages
    await pyodide.loadPackage('micropip');
    await pyodide.runPythonAsync(`
        import micropip
        await micropip.install('amplifier-core')
    `);
    
    // 3. Set up provider bridge
    // (varies by provider - see provider-specific examples)
    
    // 4. Initialize session
    await pyodide.runPythonAsync(`
        from amplifier_core import AmplifierSession
        # Session setup code
    `);
    
    return pyodide;
}
```

### With Loading Progress

```javascript
async function initWithProgress(onProgress) {
    onProgress('Loading Python runtime...', 0);
    const pyodide = await loadPyodide();
    
    onProgress('Installing packages...', 30);
    await pyodide.loadPackage('micropip');
    await pyodide.runPythonAsync(`
        import micropip
        await micropip.install('amplifier-core')
    `);
    
    onProgress('Setting up provider...', 60);
    // Provider setup...
    
    onProgress('Ready!', 100);
    return pyodide;
}
```

---

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `WebGPU not supported` | Browser lacks WebGPU | Use Chrome 113+ or API provider |
| `Out of memory` | Model too large | Use smaller model or quantization |
| `CORS error` | API blocks browser requests | Use CORS-enabled endpoint |
| `micropip.install failed` | Package not available | Check package name and availability |
| `Pyodide loading failed` | Network issue or CSP | Check network and CSP headers |

### Error Recovery

```javascript
try {
    await initAmplifier();
} catch (error) {
    if (error.message.includes('WebGPU')) {
        // Fall back to API provider
        await initWithAPIProvider();
    } else if (error.message.includes('memory')) {
        // Try smaller model
        await initWithSmallerModel();
    } else {
        // Show user-friendly error
        showError('Failed to initialize AI. Please try refreshing.');
    }
}
```

---

## Best Practices

### 1. Show Loading Progress

Users expect feedback during the ~10-30 second initialization:

```javascript
const stages = [
    'Loading Python runtime...',
    'Installing packages...',
    'Loading AI model...',
    'Ready!'
];
```

### 2. Handle Offline Gracefully

For WebLLM apps:
- Cache model in browser storage
- Show clear offline/online status
- Queue requests when offline

### 3. Secure API Keys

Never hardcode API keys:

```javascript
// BAD - key exposed in source
const apiKey = 'sk-abc123...';

// GOOD - user provides key
const apiKey = localStorage.getItem('openai_key') || prompt('Enter API key:');
```

### 4. Manage Memory

Monitor and manage memory usage:

```javascript
// Check available memory (Chrome only)
if (navigator.deviceMemory) {
    if (navigator.deviceMemory < 4) {
        console.warn('Low memory device - using smaller model');
    }
}
```

### 5. Provide Fallbacks

Not all users have WebGPU:

```javascript
async function initProvider() {
    if (await checkWebGPUSupport()) {
        return initWebLLM();
    } else {
        console.log('WebGPU not available, using API provider');
        return initAPIProvider();
    }
}
```

---

## Integration Patterns

### Single-File HTML

Everything in one file - great for sharing, demos, quick prototypes.

### ES Module App

Separate JS modules - better for larger applications.

### React/Vue/Svelte Component

Framework integration - for existing web applications.

### Web Worker

Run Amplifier in a worker - keeps UI responsive.

### Service Worker + PWA

Full offline capability - installable web app.

---

## Session Management

### In-Memory Session (Default)

Session state lives only in memory, lost on page refresh.

### Persistent Session

Use browser storage to persist across page loads:

```javascript
// Save session state
const state = await pyodide.runPythonAsync(`
    session.export_state()
`);
localStorage.setItem('amplifier_session', state);

// Restore on next load
const saved = localStorage.getItem('amplifier_session');
if (saved) {
    await pyodide.runPythonAsync(`
        session.import_state('${saved}')
    `);
}
```

---

## Debugging Tips

### Console Logging

Enable verbose logging in development:

```javascript
// Log all Amplifier events
pyodide.globals.set('debug_log', console.log);
```

### Network Tab

Check for:
- Failed model downloads
- API call errors
- CORS issues

### Memory Profiler

In Chrome DevTools:
- Memory tab shows heap usage
- Identify memory leaks
- Monitor model memory consumption

### Performance Timeline

Check initialization timing:
- Pyodide load time
- Package installation
- Model loading
