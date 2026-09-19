    )

    if is_airflow_plugin and plugin_obj.__name__ != "AirflowPlugin":
        # Validated as an AirflowPlugin subclass by name above; mypy can't narrow a name-based check.
        plugin_obj.validate()  # type: ignore[attr-defined]
        return True
    return False

