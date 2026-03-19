from typing import Any, Dict, Optional

class SharedContext:
    """
    Manages the shared state between agents.
    
    This acts as the memory or "clipboard" for the development process.
    The structure is deliberately simple (a dictionary wrapper) to allow
    flexibility as the project evolves.
    
    Example Structure:
    {
        "request": "Implement feature X",
        "explorer": { "analysis": "..." },
        "architect": { "design": "..." },
        "implementer": { "code": "..." }
    }
    """

    def __init__(self, initial_data: Optional[Dict[str, Any]] = None):
        self._data = initial_data or {}

    def get(self, key: str) -> Any:
        return self._data.get(key)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def update(self, new_data: Dict[str, Any]) -> None:
        """Merge new data into the context."""
        self._data.update(new_data)

    def to_dict(self) -> Dict[str, Any]:
        """Return the raw context dictionary."""
        return self._data.copy()

    def __str__(self) -> str:
        return str(self._data)
