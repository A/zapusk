import logging

from zapusk.models import Config, JobGroup, JobConfig

from .constants import DEFAULT_JOB_GROUPS, DEFAULT_PORT, DEFAULT_COLORS


logger = logging.getLogger(__name__)


class ConfigParser:

    @classmethod
    def parse(cls, data: dict):
        if not data:
            data = {}

        port = data.get("port", DEFAULT_PORT)
        colors = data.get("colors", DEFAULT_COLORS)
        job_groups = cls.__parse_job_groups(data.get("job_groups", {}))
        jobs = cls.__parse_jobs(data.get("jobs", []), list(job_groups.keys()))

        return Config(
            port=port,
            colors=colors,
            job_groups=job_groups,
            jobs=jobs,
        )

    @classmethod
    def __parse_job_groups(cls, data: list):
        logger.debug(f"Parsing job groups")
        if not data:
            return DEFAULT_JOB_GROUPS

        job_groups = {**DEFAULT_JOB_GROUPS}
        for v in data:
            _id = v["id"]
            job_groups[_id] = JobGroup(**v)
            logger.debug(f"Parsed {job_groups[_id]}")

        return job_groups

    @classmethod
    def __parse_jobs(cls, jobs: list, known_groups: list[str]):
        logger.debug(f"Parsing job configs")
        logger.debug(f"Known job_groups: {known_groups}")

        retval = {}
        for v in jobs:
            j = JobConfig.from_dict(v)

            if j.group not in known_groups:
                raise ValueError(f"Unknown job_group `{j.group}` in {j}")

            logger.debug(f"Parsed {j}")
            retval[v["id"]] = j

        return retval
