from unittest import TestCase
import pytest
import responses
from responses import matchers

from zapusk.client.api_client import DEFAULT_ERROR_MESSAGE, ApiClient, ApiClientError


BASE_URL = "http://localhost:4000"
api_client = ApiClient(base_url=BASE_URL)


@pytest.fixture(autouse=True)
def setUp():
    api_client = ApiClient(base_url=BASE_URL)


@responses.activate
@pytest.mark.parametrize(
    ",".join(
        [
            "method",
            "args",
            "uri",
            "status",
            "http_method",
            "matchers",
            "mocked_json",
            "expected_response",
            "expected_exception_message",
        ]
    ),
    [
        (
            "get_job",
            [1],
            "/jobs/1",
            200,
            "get",
            [],
            {"data": "OK"},
            "OK",
            None,
        ),
        (
            "get_job",
            [1],
            "/jobs/1",
            400,
            "get",
            [],
            {"error": "Error"},
            None,
            "Error",
        ),
        (
            "list_jobs",
            [],
            "/jobs/",
            200,
            "get",
            [],
            {"data": "OK"},
            "OK",
            None,
        ),
        (
            "list_jobs",
            [],
            "/jobs/",
            400,
            "get",
            [],
            {"error": "ERROR"},
            None,
            "ERROR",
        ),
        (
            "list_scheduled_jobs",
            [],
            "/scheduled-jobs/",
            200,
            "get",
            [],
            {"data": "OK"},
            "OK",
            None,
        ),
        (
            "list_scheduled_jobs",
            [],
            "/scheduled-jobs/",
            400,
            "get",
            [],
            {"error": "ERROR"},
            None,
            "ERROR",
        ),
        (
            "cancel_job",
            [1],
            "/jobs/1",
            200,
            "delete",
            [],
            {"data": "OK"},
            "OK",
            None,
        ),
        (
            "cancel_job",
            [1],
            "/jobs/1",
            400,
            "delete",
            [],
            {"error": "ERROR"},
            None,
            "ERROR",
        ),
        (
            "cancel_scheduled_job",
            [1],
            "/scheduled-jobs/1",
            200,
            "delete",
            [],
            {"data": "OK"},
            "OK",
            None,
        ),
        (
            "cancel_scheduled_job",
            [1],
            "/scheduled-jobs/1",
            400,
            "delete",
            [],
            {"error": "ERROR"},
            None,
            "ERROR",
        ),
        (
            "get_config_groups",
            [],
            "/config/groups/",
            200,
            "get",
            [],
            {"data": "OK"},
            "OK",
            None,
        ),
        (
            "get_config_groups",
            [],
            "/config/groups/",
            400,
            "get",
            [],
            {"error": "Error"},
            None,
            "Error",
        ),
        (
            "get_config_jobs",
            [],
            "/config/jobs/",
            200,
            "get",
            [],
            {"data": "OK"},
            "OK",
            None,
        ),
        (
            "get_config_jobs",
            [],
            "/config/jobs/",
            400,
            "get",
            [],
            {"error": "Error"},
            None,
            "Error",
        ),
        (
            "create_job",
            [
                {
                    "job_config_id": "echo",
                }
            ],
            "/jobs/",
            200,
            "post",
            [
                matchers.json_params_matcher(
                    {
                        "job_config_id": "echo",
                    }
                )
            ],
            {"data": "OK"},
            "OK",
            None,
        ),
        (
            "create_job",
            [
                {
                    "command": "echo 1",
                    "name": "Echo",
                    "group_id": "group",
                },
            ],
            "/jobs/",
            200,
            "post",
            [
                matchers.json_params_matcher(
                    {
                        "command": "echo 1",
                        "name": "Echo",
                        "group_id": "group",
                    }
                )
            ],
            {"data": "OK"},
            "OK",
            None,
        ),
        (
            "create_job",
            [
                {
                    "command": "echo 1",
                    "name": "Echo",
                    "group_id": "group",
                },
            ],
            "/jobs/",
            400,
            "post",
            [
                matchers.json_params_matcher(
                    {
                        "command": "echo 1",
                        "name": "Echo",
                        "group_id": "group",
                    }
                )
            ],
            {"error": "ERROR"},
            None,
            "ERROR",
        ),
        (
            "create_job",
            [
                {
                    "command": "echo 1",
                },
            ],
            "/jobs/",
            400,
            "post",
            [],
            {},
            None,
            DEFAULT_ERROR_MESSAGE,
        ),
        (
            "create_scheduled_job",
            [
                {
                    "command": "echo 1",
                    "name": "Echo",
                    "group_id": "group",
                    "schedule": "*/1 * * * *",
                }
            ],
            "/scheduled-jobs/",
            200,
            "post",
            [
                matchers.json_params_matcher(
                    {
                        "command": "echo 1",
                        "name": "Echo",
                        "group_id": "group",
                        "schedule": "*/1 * * * *",
                    }
                )
            ],
            {"data": "OK"},
            "OK",
            None,
        ),
        (
            "create_scheduled_job",
            [
                {
                    "command": "echo 1",
                    "schedule": "*/1 * * * *",
                }
            ],
            "/scheduled-jobs/",
            400,
            "post",
            [],
            {"error": "ERROR"},
            None,
            "ERROR",
        ),
    ],
    ids=[
        "get_job",
        "get_job_non_200",
        "list_jobs",
        "list_jobs_non_200",
        "list_scheduled_jobs",
        "list_scheduled_jobs_non_200",
        "cancel_job",
        "cancel_job_non_200",
        "cancel_scheduled_job",
        "cancel_scheduled_job_non_200",
        "get_config_groups",
        "get_config_groups_non_200",
        "get_config_jobs",
        "get_config_jobs_non_200",
        "create_job_from_config",
        "create_job_from_command",
        "create_job_non_200",
        "create_job_non_200_without_error_body",
        "create_scheduled_job",
        "create_scheduled_job_non_200",
    ],
)
def test_get_job(
    method,
    args,
    uri,
    status,
    http_method,
    matchers,
    mocked_json,
    expected_response,
    expected_exception_message,
):
    try:
        mocked_http_method = getattr(responses, http_method)
        mocked_http_method(
            url=f"{BASE_URL}{uri}",
            status=status,
            json=mocked_json,
            match=matchers,
        )

        mocked_method = getattr(api_client, method)
        res = mocked_method(*args)
        assert res == expected_response
    except ApiClientError as ex:
        assert ex.message == expected_exception_message


def test_exception_str():
    ex = ApiClientError("test")
    assert "test" == f"{ex}"
