from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from observatory.observatory import Observatory


async def weather_is_safe(observatory: "Observatory") -> Tuple[bool, str]:
    if not observatory.safety_monitors:
        return False, "No safety monitor configured"
    
    for safety_id, safety_monitor in observatory.safety_monitors.items():
        try:
            state_device = observatory.state.get_device(safety_id)
            if hasattr(state_device, 'safe'):
                if state_device.safe is True:
                    return True, ""
                else:
                    return False, f"Safety monitor {safety_id} reports unsafe conditions"
            else:
                return False, f"Safety monitor {safety_id} state unavailable"
        except ValueError:
            return False, f"Safety monitor {safety_id} not found in state"
    
    return False, "No safety monitor data available"


async def dome_is_open(observatory: "Observatory", dome_id: str = None) -> Tuple[bool, str]:
    if not observatory.domes:
        return False, "No dome configured"
    
    if dome_id is None:
        dome_id = next(iter(observatory.domes.keys()))
    
    if dome_id not in observatory.domes:
        return False, f"Dome {dome_id} not found"
    
    try:
        state_device = observatory.state.get_device(dome_id)
        if hasattr(state_device, 'shutter_status'):
            if state_device.shutter_status == 0:
                return True, ""
            else:
                return False, f"Dome {dome_id} is not open (status: {state_device.shutter_status})"
        else:
            return False, f"Dome {dome_id} shutter status unavailable"
    except ValueError:
        return False, f"Dome {dome_id} not found in state"
