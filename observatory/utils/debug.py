from observatory.action_registry import ActionRegistry
import time

@ActionRegistry.register("debug_print")
def debug_print(message: str):
    print(f"[DEBUG]: {message}")


@ActionRegistry.register("debug_sleep")
def debug_sleep(seconds: float):
    print(f"[DEBUG]: Sleeping for {seconds} seconds...")
    time.sleep(seconds)
    print(f"[DEBUG]: Done sleeping.")