# under the License.
from __future__ import annotations

import httpx2

from airflow.sdk.api.client import Client
from airflow.sdk.execution_time.comms import BundleInfo

FAKE_BUNDLE = BundleInfo(name="anything", version="any")


def make_client(transport: httpx2.MockTransport) -> Client:
    """Get a client with a custom transport."""
    return Client(base_url="test://server", token="", transport=transport)

    return Client(base_url=None, dry_run=True, token="")


def make_client_w_responses(responses: list[httpx2.Response]) -> Client:
    """Get a client with custom responses."""

    def handle_request(request: httpx2.Request) -> httpx2.Response:
        return responses.pop(0)

    return Client(
        base_url=None, dry_run=True, token="", mounts={"'http://": httpx2.MockTransport(handle_request)}
    )
