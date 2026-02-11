from typing import TYPE_CHECKING
import asyncio

if TYPE_CHECKING:
    from observatory.observatory import Observatory
    from observatory.state import StateManager

async def observatory_loop(state: "StateManager", observatory: "Observatory"):
    safety_threshold = 5 * observatory.safety_monitors.__len__() if observatory.safety_monitors else 5
    safety_counter = 0
    while True:
        # dumb way to have all safety monitors concur for at least 5 unsafe readings sort of
        
        shutdown_triggered = False

        if shutdown_triggered:
            await asyncio.sleep(1)
            pass
        # check safety condituions
        for safety_id, safety_monitor in observatory.safety_monitors.items():
            try:
                state_device = state.get_device(safety_id)
                if hasattr(state_device, 'safe'):
                    if state_device.safe is False:
                        print(f"Safety monitor {safety_id} reports unsafe conditions", safety_counter)
                        safety_counter += 1
                        print(safety_counter, safety_threshold)
                    else:
                        safety_counter -= 1 if safety_counter > 0 else 0
            except ValueError:
                pass

        if safety_counter >= safety_threshold and not shutdown_triggered:
            shutdown_triggered = True
            print("Safety conditions triggered emergency shutdown")
            observatory.emergency_shutdown()
        await asyncio.sleep(1)