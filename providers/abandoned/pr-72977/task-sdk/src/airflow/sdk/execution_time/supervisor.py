from uuid import UUID

import attrs
import httpx2
import msgspec
import psutil
import structlog
                    request_id=request.id,
                )
            except Exception as e:
                # Generic exception handling so a transient network error (httpx2.ConnectError /
                # httpx2.TimeoutException) or any other exception
                # doesn't crash this generator and crash the IPC communication between supervisor and task.
                log.exception(
                    "Unhandled exception while handling task request",
        yield client
        return

    limits = httpx2.Limits(max_keepalive_connections=1, max_connections=10)
    new_client = Client(base_url=server or "", limits=limits, dry_run=dry_run, token=token)
    log.debug("Connecting to execution API server", server=server)
    try:
