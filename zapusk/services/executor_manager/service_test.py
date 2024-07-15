import pytest
from unittest import mock

from .service import ExecutorManagerService


class MockBackend:
    def start(self):
        pass

    def get(self):
        pass

    def list(self):
        pass

    def add(self):
        pass

    def cancel(self):
        pass


@pytest.mark.parametrize(
    "service_method_name,backend_method_name,args,return_value",
    [
        ("get", "get", [1], {"id": 1}),
        ("list", "list", [], [1, 2, 3]),
        ("add", "add", [1], [1]),
        ("cancel", "cancel", [1], [1]),
    ],
)
def test_method_call_proxied_to_the_backend(
    service_method_name,
    backend_method_name,
    args,
    return_value,
):
    backend = MockBackend()
    setattr(
        backend,
        backend_method_name,
        mock.MagicMock(
            name=backend_method_name,
            return_value=return_value,
        ),
    )

    service = ExecutorManagerService(backend=backend)
    method = getattr(service, service_method_name)
    result = method(*args)

    mocked_method = getattr(backend, backend_method_name)
    mocked_method.assert_called_once_with(*args)

    assert result == return_value


def test_executor_manager_service_should_fail_without_backend():
    try:
        ExecutorManagerService()
    except Exception as ex:
        assert ex.args[0] == "ExecutorManagerService backend isn't configured"
