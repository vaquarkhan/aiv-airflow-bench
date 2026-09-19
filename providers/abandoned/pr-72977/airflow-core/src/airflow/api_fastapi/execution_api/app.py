)

if TYPE_CHECKING:
    import httpx2

import structlog
from structlog.contextvars import bind_contextvars
    A helper class to make it possible to run the ExecutionAPI "in-process".

    The sync version of this makes use of a2wsgi which runs the async loop in a separate thread. This is
    needed so that we can use the sync httpx2 client
    """

    _app: FastAPI | None = None

        return self._app

    # httpx2, not httpx: the only consumers are Task SDK clients, which subclass httpx2.Client,
    # and transports do not cross the httpx/httpx2 package boundary.
    @cached_property
    def transport(self) -> httpx2.WSGITransport:
        import httpx2
        from a2wsgi import ASGIMiddleware

        # We choose to own the event loop + executor thread here so that we can have explicit control over
        # safely aclose() a context whose __aenter__ has actually run.
        asyncio.run_coroutine_threadsafe(start_lifespan(cm, self.app), loop).result()

        transport = httpx2.WSGITransport(app=middleware)  # type: ignore[arg-type]

        # Stop the loop + thread and unwind the lifespan when the *transport* is garbage collected, not
        # this InProcessExecutionAPI instance. Callers commonly build a Client from ``.transport`` and drop
        return transport

    @cached_property
    def atransport(self) -> httpx2.ASGITransport:
        import httpx2

        return httpx2.ASGITransport(app=self.app)
