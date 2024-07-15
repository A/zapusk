import yaml


class YamlFileReader:
    def read(self, file) -> dict:  # type: ignore
        """
        Reads YAML file as a dict
        """
        with open(file) as stream:
            return yaml.safe_load(stream)
