import yaml
from functools import partial
from observatory.observation_engine import Sequence, ParallelGroup, Task, SequenceBuilder, Lifecycle
from observatory.action_registry import ActionRegistry
from observatory.observatory import Observatory
import inspect
from observatory import get_observatory

class SequenceParser(SequenceBuilder):
    def __init__(self, yaml_string: str, observatory: Observatory, context=None):
        self.yaml_string = yaml_string
        self.observatory = observatory
        
        data = yaml.safe_load(yaml_string)
        name = data.get("name", "Unnamed Sequence")
        description = data.get("description", name)
        
        super().__init__(name, description)
        self.context = context
        
    def build(self, yaml_string = None, context = None, observatory = None, **kwargs):
        if not yaml_string:
            yaml_string = self.yaml_string
        data = yaml.safe_load(yaml_string)

        return self._recursive_build(data, context)

    def _recursive_build(self, data: dict, context):
        name = data.get("name", "Unnamed")

        lifecycle = Lifecycle()
        if "delay" in data:
            lifecycle.hooks["delay"] = data["delay"]
        #if "before" in data:
        #     lifecycle.hooks["before"].append(partial(self._run_hook, data["before"], context))
        # if "after" in data:
        #     lifecycle.hooks["after"].append(partial(self._run_hook, data["after"], context))
        # if "finally" in data:
        #     lifecycle.hooks["finally"].append(partial(self._run_hook, data["finally"], context))
        # if "on_error" in data:
        #     lifecycle.hooks["on_error"].append(partial(self._run_hook, data["on_error"], context))
        # if "when" in data:
        #     lifecycle.hooks["when"].append(partial(self._evaluate_condition, data["when"], context))
        if "repeat" in data:
            lifecycle.hooks["repeat"] = data["repeat"]

        if "sequence" in data:
            sequence = Sequence(name, context, hooks=lifecycle)
            for step_data in data["sequence"]:
                child = self._recursive_build(step_data, context)
                sequence.add_step(child)
            return sequence
        
        elif "parallel" in data:
            parallel_group = ParallelGroup(name, context, hooks=lifecycle)
            for step_data in data["parallel"]:
                child = self._recursive_build(step_data, context)
                parallel_group.add_task(child)
            return parallel_group
        
        elif "action" in data:
            # explicitly False out observatory_arg because i'm confused
            _observatory_arg = False
            action_name = data["action"]
            args = dict(data.get("args", {}))

            func, _observatory_arg, action_type = ActionRegistry.get_action(action_name)

            original = inspect.unwrap(func)
            original_signature = inspect.signature(original)

            accepted_args = {
                key: value for key, value in args.items()
                if key in original_signature.parameters
            }
            if "observatory" in original_signature.parameters:
                print("Adding observatory to accepted args for action:", action_name)
                accepted_args["observatory"] = self.observatory

            if action_type == "device":
                device_id = data.get("device") or args.get("device")
                if not device_id:
                    raise ValueError(f"Device action '{action_name}' requires 'device' argument")
                device = self.observatory.get_device(device_id)
                bound = partial(func, device, **accepted_args)
            elif action_type == "observatory":
                bound = partial(func, self.observatory, **accepted_args)
            else:
                bound = partial(func, **accepted_args)
            
            return Task(action_name, bound, context, lifecycle)
        
        else:
            raise ValueError("Unknown node type")
