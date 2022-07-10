import toml


class Config(dict):
    def __getattribute__(self, item):
        return super().__getitem__(item)

    def __setattr__(self, key, value):
        return super().__setitem__(key, value)

    def __delattr__(self, item):
        return super().__delattr__(item)

    @classmethod
    def load_from_file(cls, filename: str) -> 'Config':
        with open(filename, encoding='utf-8') as raw_config:
            config = toml.load(raw_config)
            return cls(**config)
