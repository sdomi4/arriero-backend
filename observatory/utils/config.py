import yaml, os

def load_device_config(device: str = None):
    base_path = os.path.dirname(os.path.dirname(__file__))
    config_path = os.path.join(base_path, "config.yaml")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    return config.get(device, {})

def load_observatory_config():
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    config_path = os.path.join(base_path, "config.yaml")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    return config