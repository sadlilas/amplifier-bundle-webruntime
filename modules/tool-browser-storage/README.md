# tool-browser-storage

Browser storage tool for Amplifier - provides localStorage and IndexedDB access for browser-based applications.

## Overview

This tool enables persistent storage in browser-based Amplifier applications. It bridges Python code running in Pyodide to JavaScript's storage APIs.

## Installation

This module is included with `amplifier-bundle-browser`. To use it standalone:

```yaml
tools:
  - module: tool-browser-storage
    source: git+https://github.com/microsoft/amplifier-bundle-browser@main#subdirectory=modules/tool-browser-storage
```

## JavaScript Bridge Setup

Before using this tool, JavaScript must set up the storage bridge functions:

```javascript
// Create bridge functions
const storageBridge = {
    get: async (key) => localStorage.getItem(key),
    set: async (key, value) => localStorage.setItem(key, value),
    delete: async (key) => localStorage.removeItem(key),
    list: async () => Object.keys(localStorage),
    clear: async (prefix) => {
        Object.keys(localStorage)
            .filter(k => k.startsWith(prefix))
            .forEach(k => localStorage.removeItem(k));
    }
};

// Register with Python
pyodide.runPython(`
    from amplifier_module_tool_browser_storage import set_storage_bridge
    set_storage_bridge(
        js.storageBridge.get,
        js.storageBridge.set,
        js.storageBridge.delete,
        js.storageBridge.list,
        js.storageBridge.clear
    )
`);
```

## Tool Operations

### get

Retrieve a stored value by key.

```
browser_storage(operation="get", key="user_prefs")
```

### set

Store a value with a key.

```
browser_storage(operation="set", key="user_prefs", value='{"theme": "dark"}')
```

### delete

Remove a stored value.

```
browser_storage(operation="delete", key="user_prefs")
```

### list

List all stored keys (with the configured prefix).

```
browser_storage(operation="list")
```

### clear

Remove all stored data (with the configured prefix).

```
browser_storage(operation="clear")
```

## Configuration

```yaml
tools:
  - module: tool-browser-storage
    source: browser:modules/tool-browser-storage
    config:
      prefix: "myapp_"  # Key prefix for namespacing (default: "amplifier_")
      backend: "auto"    # "auto", "localStorage", or "indexedDB" (default: "auto")
```

## Storage Limits

- **localStorage**: ~5-10MB per origin
- **IndexedDB**: Much larger, varies by browser

## Security Notes

- Data is stored client-side and can be inspected by users
- Do not store sensitive information (API keys, passwords) without encryption
- Storage is origin-bound (same-origin policy)
