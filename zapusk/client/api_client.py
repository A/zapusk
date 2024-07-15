from collections.abc import Mapping
from typing import NotRequired, Optional, TypedDict
from urllib.parse import urljoin
import requests

from zapusk.lib.json_serdes import JsonSerdes

DEFAULT_ERROR_MESSAGE = "Server respond with an error"


class ApiClientError(Exception):
    """
    Base class for ApiClient exceptions
    """

    def __init__(self, message, *args, **kwargs) -> None:
        self.message = message
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.message}"


class JobCreateFromConfigPayload(TypedDict):
    job_config_id: str


class JobCreateFromCommandPayload(TypedDict):
    command: str
    cwd: str
    name: NotRequired[Optional[str]]
    group_id: NotRequired[Optional[str]]


class JobCreateScheduledPayload(JobCreateFromCommandPayload):
    schedule: str


class ApiClient:
    http_client = requests

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def __filter_none(self, d: Mapping):
        return {k: v for k, v in d.items() if v is not None}

    def __handle_error(self, res):
        body = res.json()
        if "error" in res.json():
            raise ApiClientError(body["error"])
        else:
            raise ApiClientError(DEFAULT_ERROR_MESSAGE)

    def get_job(self, job_id: str | int):
        res = self.http_client.get(urljoin(self.base_url, f"/jobs/{job_id}"))
        body = res.json()

        if res.status_code != 200:
            return self.__handle_error(res)

        return JsonSerdes.deserialize(body)

    def list_jobs(self):
        res = self.http_client.get(urljoin(self.base_url, f"/jobs/"))
        body = res.json()

        if res.status_code != 200:
            return self.__handle_error(res)

        return JsonSerdes.deserialize(body)

    def list_scheduled_jobs(self):
        res = self.http_client.get(urljoin(self.base_url, f"/scheduled-jobs/"))
        body = res.json()

        if res.status_code != 200:
            return self.__handle_error(res)

        return JsonSerdes.deserialize(body)

    def create_job(
        self, payload: JobCreateFromConfigPayload | JobCreateFromCommandPayload
    ):
        res = requests.post(
            urljoin(self.base_url, "/jobs/"),
            json=self.__filter_none(payload),
        )

        if res.status_code != 200:
            return self.__handle_error(res)

        return JsonSerdes.deserialize(res.json())

    def create_scheduled_job(self, payload: JobCreateScheduledPayload):
        res = requests.post(
            urljoin(self.base_url, "/scheduled-jobs/"),
            json=self.__filter_none(payload),
        )
        if res.status_code != 200:
            return self.__handle_error(res)

        return JsonSerdes.deserialize(res.json())

    def cancel_job(self, job_id: str | int):
        res = self.http_client.delete(urljoin(self.base_url, f"/jobs/{job_id}"))
        body = res.json()

        if res.status_code != 200:
            return self.__handle_error(res)

        return JsonSerdes.deserialize(body)

    def cancel_scheduled_job(self, job_id: str | int):
        res = self.http_client.delete(
            urljoin(self.base_url, f"/scheduled-jobs/{job_id}")
        )
        body = res.json()

        if res.status_code != 200:
            return self.__handle_error(res)

        return JsonSerdes.deserialize(body)

    def get_config_groups(self):
        res = self.http_client.get(urljoin(self.base_url, f"/config/groups/"))
        body = res.json()

        if res.status_code != 200:
            return self.__handle_error(res)

        return JsonSerdes.deserialize(body)

    def get_config_jobs(self):
        res = self.http_client.get(urljoin(self.base_url, f"/config/jobs/"))
        body = res.json()

        if res.status_code != 200:
            return self.__handle_error(res)

        return JsonSerdes.deserialize(body)
