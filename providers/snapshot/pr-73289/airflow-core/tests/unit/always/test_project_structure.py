            "providers/snowflake/tests/unit/snowflake/triggers/test_snowflake_trigger.py",
            "providers/standard/tests/unit/standard/operators/test_empty.py",
            "providers/standard/tests/unit/standard/sensors/test_external_task.py",
        ]
        modules_files: list[pathlib.Path] = list(
            AIRFLOW_PROVIDERS_ROOT_PATH.glob("**/src/airflow/providers/**/*.py")
