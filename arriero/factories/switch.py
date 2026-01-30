from alpaca import switch
from time import sleep

from observatory.state import StateManager, SwitchState, ToggleControl, RangeControl

class SwitchConnectionError(RuntimeError):
    pass


def switch_factory(
        address: str,
        id: str,
        device_number: int = 0,
        state: "StateManager" = None,
    ) -> switch.Switch:
    try:
        print("connecting to switch", id, address)
        s = switch.Switch(address, device_number)
        timeout = 0
        s.Connect()
        while s.Connecting:
                timeout += 1
                if timeout > 10:
                    print("Switch connection timed out")
                    raise SwitchConnectionError("Switch connection timed out")
                sleep(1)
        
        # Initialize switch controls
        controls = {}
        for i in range(s.MaxSwitch):
            switch_name = s.GetSwitchName(i)
            can_write = s.CanWrite(i)
            
            # Determine if it's a toggle or range control
            try:
                min_val = s.MinSwitchValue(i)
                max_val = s.MaxSwitchValue(i)
                step_val = s.SwitchStep(i)
                value = s.GetSwitchValue(i)
                
                controls[switch_name] = RangeControl(
                    id=i,
                    label=switch_name,
                    writeable=can_write,
                    min_value=min_val,
                    max_value=max_val,
                    step=step_val,
                    value=value
                )
            except:
                # If range methods fail, treat as toggle
                value = s.GetSwitch(i)
                controls[switch_name] = ToggleControl(
                    id=i,
                    label=switch_name,
                    writeable=can_write,
                    value=value
                )
        
        state.add_device(SwitchState(id=id, connected=True, controls=controls))
        return s
    except Exception as e:
        print(f"Error connecting to switch: {e}")
        raise SwitchConnectionError(f"Error connecting to switch: {e}")