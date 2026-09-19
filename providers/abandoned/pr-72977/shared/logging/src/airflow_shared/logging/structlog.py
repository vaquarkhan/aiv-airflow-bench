    # structlog to ignore.

    import contextlib
    import importlib

    import click

    suppress: tuple[ModuleType, ...] = (click, contextlib)
    # airflow-core is still on httpx while the Task SDK is on httpx2, so either (or both) may
    # be installed; tracked at https://github.com/apache/airflow/issues/70522
    for module_name in ("httpcore", "httpcore2", "httpx", "httpx2"):
        with contextlib.suppress(ImportError):
            suppress = (*suppress, importlib.import_module(module_name))

    if json_output:
        dict_exc_formatter = structlog.tracebacks.ExceptionDictTransformer(
            "airflow": {"level": log_level.upper()},
            # These ones are too chatty even at info
            "httpx": {"level": "WARN"},
            "httpx2": {"level": "WARN"},
            "sqlalchemy.engine": {"level": "WARN"},
            "alembic.runtime.plugins": {"level": "WARN"},
        }
