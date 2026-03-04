import yaml
from functools import partial
from observatory.observation_engine import Sequence, ParallelGroup, Task, SequenceBuilder
from observatory.action_registry import ActionRegistry
from observatory.observatory import Observatory

from observatory import get_observatory

class SequenceParser(SequenceBuilder):
    def __init__(self, yaml_string: str, observatory: Observatory = None, context=None):
        self.yaml_string = yaml_string
        self.observatory = observatory
        
        data = yaml.safe_load(yaml_string)
        name = data.get("name", "Unnamed Sequence")
        description = data.get("description", name)
        
        super().__init__(name, description)
        self.context = context
        
    def build(self, yaml_string = None, edict = None, observatory = None):
        if not yaml_string:
            yaml_string = self.yaml_string
        data = yaml.safe_load(yaml_string)

        return self._recursive_build(data, edict)

    def _recursive_build(self, data: dict, edict):
        name = data.get("name", "Unnamed")

        if "sequence" in data:
            sequence = Sequence(name, edict)
            for step_data in data["sequence"]:
                child = self._recursive_build(step_data, edict)
                sequence.add_step(child)
            return sequence
        
        elif "parallel" in data:
            parallel_group = ParallelGroup(name, edict)
            for step_data in data["parallel"]:
                child = self._recursive_build(step_data, edict)
                parallel_group.add_task(child)

            return parallel_group
        
        elif "action" in data:
            action_name = data["action"]
            args = data.get("args", {})

            device_id = args.pop("device_id", None)
            if device_id:
                device = self.observatory.devices[device_id]

            func = ActionRegistry.get_action(action_name)
            bound = partial(func, self.observatory, **args)

            return Task(action_name, bound, edict)
        
        else:
            raise ValueError("Unknown node type")