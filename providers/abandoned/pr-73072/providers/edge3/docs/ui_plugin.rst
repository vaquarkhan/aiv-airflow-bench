configure the remote workers (Technical key: AccessView.JOBS). With this permission you can also manage
the workers like adjusting queues, concurrency, set them to maintenance mode or shutdown the workers.

.. warning::

    "can read on Jobs" (``AccessView.JOBS``) is the **management** permission for Edge workers, not a
    read-only one. It is deliberately the single permission gating the whole plugin, and the worker
    management endpoints under ``/edge_worker/ui/`` check only this permission -- the HTTP method is not
    part of the check. "can read on Plugins" governs only whether the plugin appears in the UI
    navigation; it is not required in order to call the endpoints.

    A principal holding "can read on Jobs" can therefore shut down, delete, re-queue and retune Edge
    workers by calling those endpoints directly, whether or not the plugin is visible to them.

    This matters for the default ``Viewer`` role, which **includes "can read on Jobs"**. In a default
    Flask AppBuilder setup a Viewer does not see the Edge plugin in the navigation (Viewer has no
    "can read on Plugins"), but can still reach the worker management endpoints. If Viewers in your
    deployment must not manage Edge workers, remove "can read on Jobs" from that role or give those
    users a custom role without it.

    Finer-grained separation of read and management permissions for Edge workers is not implemented;
    it is listed under :doc:`architecture` as a known missing feature.

Note that maintenance mode can also be adjusted via CLI.
See :ref:`deployment:maintenance` for more details.
