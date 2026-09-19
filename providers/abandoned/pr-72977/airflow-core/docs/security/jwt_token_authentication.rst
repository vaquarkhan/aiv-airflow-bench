2. The workload JSON is passed to the worker process (via the executor-specific mechanism:
   Celery message, Kubernetes Pod spec, local subprocess arguments, etc.).
3. The worker's ``execute_workload()`` function reads the workload JSON and extracts the token.
4. The ``supervise_task()`` function receives the token and creates an ``httpx2.Client`` instance
   with ``BearerAuth(token)`` for all Execution API HTTP requests.
5. The worker calls the ``/run`` endpoint with the ``workload``-scoped token to mark the task
   as running. The server responds with a fresh ``execution``-scoped token in the
