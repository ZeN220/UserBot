import toml


class Config(dict):
    def __init__(self, config_dict: dict):
        super().__init__()
        for key, value in config_dict.items():
            if isinstance(value, dict):
                value = Config(value)
            self[key] = value

    def __getattr__(self, item):
        return super().__getitem__(item)

    def __setattr__(self, key, value):
        return super().__setitem__(key, value)

    def __delattr__(self, item):
        return super().__delattr__(item)

    @classmethod
    def load_from_file(cls, filename: str) -> 'Config':
        with open(filename, encoding='utf-8') as raw_config:
            raw_config = toml.load(raw_config)
            return cls(raw_config)
