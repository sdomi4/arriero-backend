from typing import Callable, Dict

class ActionRegistry:
    _actions: Dict[str, Callable] = {}

    @classmethod
    def register(cls, name, observatory_arg=False, action_type=None):
        """Decorator to register a function"""
        def decorator(func):
            cls._actions[name] = (func, observatory_arg, action_type)
            return func
        return decorator

    @classmethod
    def get_action(cls, name):
        if name not in cls._actions:
            raise ValueError(f"Unknown action: {name}")
        return cls._actions[name]
    
    @classmethod
    def list_actions(cls):
        return list(cls._actions.keys())