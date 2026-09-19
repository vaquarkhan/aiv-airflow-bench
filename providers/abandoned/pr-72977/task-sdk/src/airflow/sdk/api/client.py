from urllib.parse import quote

import certifi
import httpx2
import msgspec
import structlog
from opentelemetry import trace
]


def get_json_error(response: httpx2.Response):
    """Raise a ServerResponseError if we can extract error info from the error."""
    err = ServerResponseError.from_response(response)
    if err:
        raise err


def raise_on_4xx_5xx(response: httpx2.Response):
    return get_json_error(response) or response.raise_for_status()


# Py 3.11+ version
def raise_on_4xx_5xx_with_note(response: httpx2.Response):
    try:
        return get_json_error(response) or response.raise_for_status()
    except httpx2.HTTPStatusError as e:
        if TYPE_CHECKING:
            assert hasattr(e, "add_note")
        e.add_note(
    raise_on_4xx_5xx = raise_on_4xx_5xx_with_note


def add_correlation_id(request: httpx2.Request):
    request.headers["correlation-id"] = str(uuid7())


def inject_trace_context(request: httpx2.Request) -> None:
    _trace_propagator.inject(request.headers)


        self.client.patch(f"callbacks/{callback_id}/run")


class BearerAuth(httpx2.Auth):
    def __init__(self, token: str):
        self.token: str = token

    def auth_flow(self, request: httpx2.Request):
        if self.token:
            request.headers["Authorization"] = "Bearer " + self.token
        yield request


# This exists as an aid for debugging or local running via the `dry_run` argument to Client. It doesn't make
# sense for returning connections etc.
def noop_handler(request: httpx2.Request) -> httpx2.Response:
    path = request.url.path
    log.debug("Dry-run request", method=request.method, path=path)

    if path.startswith("/task-instances/") and path.endswith("/run"):
        # Return a fake context
        return httpx2.Response(
            200,
            json={
                "dag_run": {
                "should_retry": False,
            },
        )
    return httpx2.Response(200, json={"text": "Hello, world!"})


# Note: Given defaults make attempts after 1, 3, 7, 15 and fails after 31seconds

def _should_retry_api_request(exception: BaseException) -> bool:
    """Determine if an API request should be retried based on the exception type."""
    if isinstance(exception, httpx2.HTTPStatusError):
        return exception.response.status_code >= 500

    return isinstance(exception, httpx2.RequestError)


class Client(httpx2.Client):
    @lru_cache()
    @staticmethod
    def _get_ssl_context_cached(ca_file: str | None = None, ca_path: str | None = None) -> ssl.SSLContext:
        if dry_run:
            # If dry run is requested, install a no op handler so that simple tasks can "heartbeat" using a
            # real client, but just don't make any HTTP requests
            kwargs.setdefault("transport", httpx2.MockTransport(noop_handler))
            kwargs.setdefault("base_url", "dry-run://server")
        else:
            kwargs["base_url"] = base_url
            **kwargs,
        )

    def _update_auth(self, response: httpx2.Response):
        if new_token := response.headers.get("Refreshed-API-Token"):
            log.debug("Execution API issued us a refreshed Task token")
            self.auth = BearerAuth(new_token)
        reraise=True,
    )
    def request(self, *args, **kwargs):
        """Implement a convenience for httpx2.Client.request with a retry layer."""
        # Set content type as convenience if not already set
        if kwargs.get("content", None) is not None and "content-type" not in (
            kwargs.get("headers", {}) or {}
        return repr(self.detail)


class ServerResponseError(httpx2.HTTPStatusError):
    def __init__(self, message: str, *, request: httpx2.Request, response: httpx2.Response):
        super().__init__(message, request=request, response=response)

    detail: list[RemoteValidationError] | str | dict[str, Any] | None

    def __reduce__(self) -> tuple[Any, ...]:
        # Needed because https://github.com/encode/httpx/pull/3108 never landed, and httpx2
        # forked from httpx 0.28.1 without it.
        return Exception.__new__, (type(self),) + self.args, self.__dict__

    @classmethod
    def from_response(cls, response: httpx2.Response) -> ServerResponseError | None:
        if response.is_success:
            return None
        # 4xx or 5xx error?
            try:
                detail = msgspec.json.decode(response.content)
            except Exception:
                # Fallback to a normal httpx2 error
                return None
            msg = "Server returned error"

