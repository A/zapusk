import logging
import os
from os.path import isfile
from typing import Optional, cast

from zapusk.models.job_group import JobGroup
from .config_parser import ConfigParser
from .yaml_filereader import YamlFileReader


logger = logging.getLogger(__name__)


class ConfigService:
    config_path: str

    def __init__(
        self,
        config_path: Optional[str] = None,
        file_reader=YamlFileReader(),
        parser=ConfigParser(),
    ):
        self.file_reader = file_reader
        self.parser = parser
        self.config_path = self.__get_config_path(config_path)

    def __get_config_path(self, config_path):
        """
        Returns a path to the config file considering evnironment configuration
        """
        if config_path:
            return os.path.expanduser(config_path)

        config_dir = os.path.join(
            os.environ.get("APPDATA")
            or os.environ.get("XDG_CONFIG_HOME")
            or os.path.join(os.environ["HOME"], ".config"),
            "zapusk",
        )

        logger.info(f"Config Dir: {config_dir}")

        logger.debug(f"Try to load config file: {config_dir}/config.yaml")
        if isfile(f"{config_dir}/config.yaml"):
            logger.debug(f"Loaded config file: {config_dir}/config.yaml")
            return f"{config_dir}/config.yaml"

        logger.debug(f"Try to load config file: {config_dir}/config.yml")
        if isfile(f"{config_dir}/config.yml"):
            logger.debug(f"Loaded config file: {config_dir}/config.yml")
            return f"{config_dir}/config.yml"
        else:
            raise FileExistsError("Config not found")

    def get_config(self):
        config = self.file_reader.read(self.config_path)
        return self.parser.parse(config)

    def list_jobs(self):
        config = self.get_config()
        return list(config.jobs.values())

    def list_jobgroups(self):
        config = self.get_config()
        return list(config.job_groups.values())

    def get_job(self, job_id: str):
        config = self.get_config()

        for job in config.jobs.values():
            if job.id == job_id:
                return job

        return None

    def get_job_group(self, job_group_id: str):
        config = self.get_config()

        for job_group in config.job_groups.values():
            if job_group.id == job_group_id:
                return job_group

        return None

    def get_job_group_or_default(self, job_group_id: str):
        job_group = self.get_job_group(job_group_id)

        if not job_group:
            job_group = cast(JobGroup, self.get_job_group("default"))

        return job_group
