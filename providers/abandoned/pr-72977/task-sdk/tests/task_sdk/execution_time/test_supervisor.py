from unittest import mock
from unittest.mock import MagicMock, patch

import httpx2
import msgspec
import psutil
import pytest
        main_pid = os.getpid()
        ti_id = "4d828a62-a417-4936-a7a6-2b3fabacecab"

        def handle_request(request: httpx2.Request) -> httpx2.Response:
            if request.url.path == f"/task-instances/{ti_id}/heartbeat":
                return httpx2.Response(
                    status_code=409,
                    json={
                        "detail": {
                    },
                )
            if request.url.path == f"/task-instances/{ti_id}/run":
                return httpx2.Response(200, json=make_ti_context_dict())
            return httpx2.Response(status_code=204)

        def subprocess_main():
            # Ensure we follow the "protocol" and get the startup message before we do anything
                dag_version_id=uuid7(),
                queue="default",
            ),
            client=make_client(transport=httpx2.MockTransport(handle_request)),
            target=subprocess_main,
        )

        # Track the number of requests to simulate mixed responses
        request_count = {"count": 0}

        def handle_request(request: httpx2.Request) -> httpx2.Response:
            if request.url.path == f"/task-instances/{ti_id}/heartbeat":
                request_count["count"] += 1
                if request_count["count"] == 1:
                    # First request succeeds
                    return httpx2.Response(status_code=204)
                # Second request returns a conflict status code
                return httpx2.Response(
                    409,
                    json={
                        "reason": "not_running",
                    },
                )
            if request.url.path == f"/task-instances/{ti_id}/run":
                return httpx2.Response(200, json=make_ti_context_dict())
            if request.url.path == f"/task-instances/{ti_id}/state":
                pytest.fail("Should not have sent a state update request")
            # Return a 204 for all other requests
            return httpx2.Response(status_code=204)

        proc = ActivitySubprocess.start(
            dag_rel_path=os.devnull,
                dag_version_id=uuid7(),
                queue="default",
            ),
            client=make_client(transport=httpx2.MockTransport(handle_request)),
            target=subprocess_main,
            bundle_info=FAKE_BUNDLE,
        )
        when the API returns 409 with previous_state='running'."""
        ti_id = uuid7()

        def handle_request(request: httpx2.Request) -> httpx2.Response:
            if request.url.path == f"/task-instances/{ti_id}/run":
                return httpx2.Response(
                    409,
                    json={
                        "detail": {
                        }
                    },
                )
            return httpx2.Response(status_code=204)

        def subprocess_main():
            # Ensure we follow the "protocol" and get the startup message before we do anything
                    dag_version_id=uuid7(),
                    queue="default",
                ),
                client=make_client(transport=httpx2.MockTransport(handle_request)),
                target=subprocess_main,
            )


        error = ServerResponseError(
            message="API Server Error",
            request=httpx2.Request("GET", "http://test"),
            response=httpx2.Response(500, json={"detail": "Internal Server Error"}),
        )

        mock_client_method = mocker.Mock(side_effect=error)

        error = ServerResponseError(
            message="boom",
            request=httpx2.Request("PUT", "http://test"),
            response=httpx2.Response(status_code, json={"detail": "boom"}),
        )
        watched_subprocess.client.task_instances.set_rtif = mocker.Mock(side_effect=error)

    def test_handle_requests_network_exception_does_not_crash_loop(self, watched_subprocess, mocker):
        """A transient network error must not crash the IPC generator.

        Without the catch-all in handle_requests, an httpx2.ConnectError would
        propagate, the generator would terminate, the task subprocess would
        get EOFError on every subsequent send, and the worker would be stuck.
        Verify that the error is reported back to the task as an
        watched_subprocess, read_socket = watched_subprocess

        # First request raises a network exception, second succeeds.
        first_call = httpx2.ConnectError("connection refused")
        watched_subprocess.client.task_instances.succeed = mocker.Mock(side_effect=[first_call, None])

        generator = watched_subprocess.handle_requests(log=mocker.Mock())
        setattr(
            watched_subprocess.client.task_instances,
            api_method,
            mocker.Mock(side_effect=httpx2.ConnectError("connection refused")),
        )

        with pytest.raises(httpx2.ConnectError):
            watched_subprocess._handle_request(msg, mocker.Mock(), req_id=1)

        assert watched_subprocess._terminal_state is None
    def test_no_retries(self):
        called = 0

        def noop_handler(request: httpx2.Request) -> httpx2.Response:
            nonlocal called
            called += 1
            return httpx2.Response(500)

        transport = httpx2.MockTransport(noop_handler)
        client = InProcessTestSupervisor._Client(
            base_url="http://local.invalid", token="", transport=transport
        )

        with pytest.raises(httpx2.HTTPStatusError):
            client.get("/goo")

        assert called == 1
    monkeypatch.delitem(sys.modules, "airflow.config_templates.airflow_local_settings", raising=False)
    monkeypatch.delitem(sys.modules, "airflow.sdk.log", raising=False)

    def handle_request(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(
            status_code=200,
            json={
                # Minimal enough to pass validation, we don't care what fields are in here for the tests
            }
        ):
            env = os.environ.copy()
            client = make_client(transport=httpx2.MockTransport(handle_request))

            with _remote_logging_conn(client):
                new_keys = os.environ.keys() - env.keys()
    mocker.patch.object(
        ActivitySubprocess,
        "update_task_state_if_needed",
        side_effect=httpx2.ConnectError("connection refused"),
    )
    upload_logs = mocker.patch.object(ActivitySubprocess, "_upload_logs")

    with pytest.raises(httpx2.ConnectError):
        proc.wait()

    upload_logs.assert_called_once_with()
    conn_id = "s3_conn_logs"
    conn_uri = "aws:///?region_name=us-east-1"

    def handle_request(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(
            status_code=200,
            json={
                "conn_id": conn_id,
                ("logging", "remote_log_conn_id"): conn_id,
            }
        ):
            client = make_client(transport=httpx2.MockTransport(handle_request))

            assert os.getenv("_AIRFLOW_PROCESS_CONTEXT") is None

        }
    ):

        def noop_request(request: httpx2.Request) -> httpx2.Response:
            return httpx2.Response(200)

        clients = []
        for _ in range(3):
            client = make_client(transport=httpx2.MockTransport(noop_request))
            clients.append(weakref.ref(client))
            with _remote_logging_conn(client):
                pass
