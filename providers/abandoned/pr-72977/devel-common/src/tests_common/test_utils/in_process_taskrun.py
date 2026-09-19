
def _remembering_handler(store: dict, run_context_json: bytes) -> Callable:
    """A dry-run transport handler: valid run-context + XCom round-trip from ``store``, else no-op."""
    import httpx2

    from airflow.sdk.api.client import noop_handler

    def handler(request: httpx2.Request) -> httpx2.Response:
        path = request.url.path
        if path.startswith("/task-instances/") and path.endswith("/run"):
            return httpx2.Response(200, content=run_context_json)
        parts = path.strip("/").split("/")
        if len(parts) == _XCOM_PATH_PARTS and parts[0] == "xcoms":
            dag_id, run_id, task_id, key = parts[1:]
            sig = (dag_id, run_id, task_id, key)
            if request.method == "POST":
                store[sig] = json.loads(request.content)
                return httpx2.Response(201, json={"ok": True})
            if request.method == "GET":
                if sig in store:
                    return httpx2.Response(200, json={"key": key, "value": store[sig]})
                return httpx2.Response(404, json={"detail": "XCom not found"})
        return noop_handler(request)

    return handler
    ``ti_context`` (a ``TIRunContext``) is replayed for the task-start request. Pushed XCom
    values are exposed as ``client.pushed_xcoms`` keyed by ``(dag_id, run_id, task_id, key)``.
    """
    import httpx2

    from airflow.sdk.api.client import Client

        base_url=None,
        dry_run=True,
        token="",
        transport=httpx2.MockTransport(_remembering_handler(store, ti_context.model_dump_json().encode())),
    )
    client.pushed_xcoms = store  # type: ignore[attr-defined]
    return client
