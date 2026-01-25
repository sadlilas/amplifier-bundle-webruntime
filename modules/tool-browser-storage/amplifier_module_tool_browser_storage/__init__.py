"""Browser storage tool for Amplifier.

Provides localStorage and IndexedDB access for browser-based Amplifier applications.
This tool is designed to run in Pyodide (Python in WebAssembly) and bridges to
JavaScript storage APIs.
"""

from .tool import BrowserStorageTool

# The storage bridge functions - set by JavaScript before tool is used
_js_storage_get = None
_js_storage_set = None
_js_storage_delete = None
_js_storage_list = None
_js_storage_clear = None


def set_storage_bridge(get_fn, set_fn, delete_fn, list_fn, clear_fn):
    """Set the JavaScript bridge functions for storage operations.

    This must be called from JavaScript before using the storage tool.

    Example JavaScript setup:
        pyodide.runPython(`
            from amplifier_module_tool_browser_storage import set_storage_bridge
            set_storage_bridge(
                js_storage_get,
                js_storage_set,
                js_storage_delete,
                js_storage_list,
                js_storage_clear
            )
        `)
    """
    global \
        _js_storage_get, \
        _js_storage_set, \
        _js_storage_delete, \
        _js_storage_list, \
        _js_storage_clear
    _js_storage_get = get_fn
    _js_storage_set = set_fn
    _js_storage_delete = delete_fn
    _js_storage_list = list_fn
    _js_storage_clear = clear_fn


def get_bridge():
    """Get the current storage bridge functions."""
    return {
        "get": _js_storage_get,
        "set": _js_storage_set,
        "delete": _js_storage_delete,
        "list": _js_storage_list,
        "clear": _js_storage_clear,
    }


async def mount(coordinator, config: dict):
    """Mount the browser storage tool.

    Args:
        coordinator: The Amplifier coordinator
        config: Tool configuration
            - prefix: Key prefix for namespacing (default: "amplifier_")
            - backend: Storage backend - "auto", "localStorage", "indexedDB" (default: "auto")
    """
    tool = BrowserStorageTool(config)
    coordinator.mount_points["tools"][tool.name] = tool
    return None  # No cleanup needed
