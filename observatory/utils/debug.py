from observatory.action_registry import ActionRegistry
import time

@ActionRegistry.register("debug_print", observatory_arg=False, action_type="debug")
def debug_print(message: str):
    print(f"[DEBUG]: {message}")


@ActionRegistry.register("debug_sleep", observatory_arg=False, action_type="debug")
def debug_sleep(seconds: float):
    print(f"[DEBUG]: Sleeping for {seconds} seconds...")
    time.sleep(seconds)
    print(f"[DEBUG]: Done sleeping.")

@ActionRegistry.register("debug_timestamp", observatory_arg=False, action_type="debug")
def debug_timestamp():
    # human readable timestamp
    print(f"[DEBUG]: Current timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")