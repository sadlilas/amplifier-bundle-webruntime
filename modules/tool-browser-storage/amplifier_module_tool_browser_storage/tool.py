"""Browser storage tool implementation."""

import json

from amplifier_core.protocols import Tool, ToolResult

from . import get_bridge


class BrowserStorageTool(Tool):
    """Tool for browser storage operations (localStorage/IndexedDB).

    This tool bridges to JavaScript storage APIs via functions set up
    by the browser environment. It provides a simple key-value interface
    for persistent storage in browser-based Amplifier applications.
    """

    name = "browser_storage"
    description = """Browser storage operations for persistent data in browser-based Amplifier.

Use this tool to store and retrieve data that persists across page loads.
Data is stored in the browser's localStorage or IndexedDB.

Operations:
- get: Retrieve a stored value by key
- set: Store a value with a key
- delete: Remove a stored value
- list: List all stored keys
- clear: Remove all stored data

Note: Storage is limited to the current browser origin (domain).
localStorage has ~5-10MB limit. IndexedDB has larger limits but varies by browser."""

    parameters = {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": ["get", "set", "delete", "list", "clear"],
                "description": "The storage operation to perform",
            },
            "key": {
                "type": "string",
                "description": "The key for get/set/delete operations",
            },
            "value": {
                "type": "string",
                "description": "The value to store (for set operation). Will be JSON-serialized if not a string.",
            },
        },
        "required": ["operation"],
    }

    def __init__(self, config: dict):
        """Initialize the browser storage tool.

        Args:
            config: Tool configuration
                - prefix: Key prefix for namespacing (default: "amplifier_")
                - backend: Storage backend hint (default: "auto")
        """
        self.prefix = config.get("prefix", "amplifier_")
        self.backend = config.get("backend", "auto")

    def _get_prefixed_key(self, key: str) -> str:
        """Add prefix to key for namespacing."""
        return f"{self.prefix}{key}"

    def _check_bridge(self) -> tuple[bool, str | None]:
        """Check if the JavaScript bridge is set up."""
        bridge = get_bridge()
        if bridge["get"] is None:
            return (
                False,
                "Storage bridge not initialized. JavaScript must call set_storage_bridge() first.",
            )
        return True, None

    async def execute(self, **kwargs) -> ToolResult:
        """Execute a storage operation."""
        operation = kwargs.get("operation")
        key = kwargs.get("key")
        value = kwargs.get("value")

        # Check bridge is set up
        bridge_ok, error = self._check_bridge()
        if not bridge_ok:
            return ToolResult(success=False, output=None, error=error)

        bridge = get_bridge()

        try:
            if operation == "get":
                if not key:
                    return ToolResult(
                        success=False,
                        output=None,
                        error="'key' is required for get operation",
                    )
                prefixed_key = self._get_prefixed_key(key)
                result = await bridge["get"](prefixed_key)

                if result is None:
                    return ToolResult(
                        success=True, output=f"No value found for key: {key}"
                    )

                # Try to parse as JSON
                try:
                    parsed = json.loads(result)
                    return ToolResult(success=True, output=json.dumps(parsed, indent=2))
                except json.JSONDecodeError:
                    return ToolResult(success=True, output=result)

            elif operation == "set":
                if not key:
                    return ToolResult(
                        success=False,
                        output=None,
                        error="'key' is required for set operation",
                    )
                if value is None:
                    return ToolResult(
                        success=False,
                        output=None,
                        error="'value' is required for set operation",
                    )

                prefixed_key = self._get_prefixed_key(key)

                # Serialize value if it's not already a string
                if not isinstance(value, str):
                    value = json.dumps(value)

                await bridge["set"](prefixed_key, value)
                return ToolResult(success=True, output=f"Stored value for key: {key}")

            elif operation == "delete":
                if not key:
                    return ToolResult(
                        success=False,
                        output=None,
                        error="'key' is required for delete operation",
                    )

                prefixed_key = self._get_prefixed_key(key)
                await bridge["delete"](prefixed_key)
                return ToolResult(success=True, output=f"Deleted key: {key}")

            elif operation == "list":
                all_keys = await bridge["list"]()

                # Filter to only keys with our prefix and strip prefix
                prefix_len = len(self.prefix)
                keys = [k[prefix_len:] for k in all_keys if k.startswith(self.prefix)]

                if not keys:
                    return ToolResult(success=True, output="No stored keys found.")

                return ToolResult(
                    success=True,
                    output=f"Stored keys ({len(keys)}):\n"
                    + "\n".join(f"  - {k}" for k in sorted(keys)),
                )

            elif operation == "clear":
                await bridge["clear"](self.prefix)
                return ToolResult(
                    success=True,
                    output=f"Cleared all storage with prefix: {self.prefix}",
                )

            else:
                return ToolResult(
                    success=False,
                    output=None,
                    error=f"Unknown operation: {operation}. Valid operations: get, set, delete, list, clear",
                )

        except Exception as e:
            return ToolResult(
                success=False, output=None, error=f"Storage operation failed: {str(e)}"
            )
