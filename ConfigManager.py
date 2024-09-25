import json
import os

class ConfigManager:
    CONFIG_FILE = os.path.expanduser("~/.config/widgetForFun/config.json")

    @classmethod
    def load_config(cls, window_name):
        if os.path.exists(cls.CONFIG_FILE):
            with open(cls.CONFIG_FILE, "r") as f:
                config = json.load(f)
        else:
            config = {}

        return config.get(window_name, {})

    @classmethod
    def save_config(cls, window_name, window_config):
        os.makedirs(os.path.dirname(cls.CONFIG_FILE), exist_ok=True)
        
        if os.path.exists(cls.CONFIG_FILE):
            with open(cls.CONFIG_FILE, "r") as f:
                config = json.load(f)
        else:
            config = {}

        config[window_name] = window_config

        with open(cls.CONFIG_FILE, "w") as f:
            json.dump(config, f)