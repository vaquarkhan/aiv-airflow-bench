from airflow.utils.deprecation_tools import add_deprecated_classes

__deprecated_classes = {
    "deadline": {
        # Moved in Airflow 3.2.0 (#57215) without a shim. Kept importable so a Trigger persisted
        # under the old classpath (a pre-3.2 scheduler, or a row predating the move) stays loadable
        # by a newer triggerer that resolves it via ``import_string``.
        "DeadlineCallbackTrigger": "airflow.triggers.callback.CallbackTrigger",
    },
    "external_task": {
        "WorkflowTrigger": "airflow.providers.standard.triggers.external_task.WorkflowTrigger",
        "DagStateTrigger": "airflow.providers.standard.triggers.external_task.DagStateTrigger",
