from typing import Callable, Dict

class ActionRegistry:
    _actions: Dict[str, Callable] = {}

    @classmethod
    def register(cls, name):
        """Decorator to register a function"""
        def decorator(func):
            cls._actions[name] = func
            return func
        return decorator

    @classmethod
    def get_action(cls, name):
        if name not in cls._actions:
            raise ValueError(f"Unknown action: {name}")
        return cls._actions[name]