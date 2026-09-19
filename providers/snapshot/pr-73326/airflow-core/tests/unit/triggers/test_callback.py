        mock_callback.assert_called_once_with(**TEST_CALLBACK_KWARGS)
        assert failure_event.payload[PAYLOAD_STATUS_KEY] == CallbackState.FAILED
        assert all(s in failure_event.payload[PAYLOAD_BODY_KEY] for s in ["raise", "RuntimeError", exc_msg])


def test_deprecated_deadline_callback_trigger_classpath_is_importable():
    """
    The pre-3.2 deadline trigger classpath must stay loadable and resolve to ``CallbackTrigger``.

    Airflow 3.2.0 (#57215) moved ``airflow.triggers.deadline.DeadlineCallbackTrigger`` to
    ``airflow.triggers.callback.CallbackTrigger`` without leaving a compatibility shim, so a
    triggerer that resolved a trigger serialized under the old classpath raised
    ``ModuleNotFoundError``. The shim in ``airflow.triggers.__init__`` keeps the old classpath
    importable (redirecting to ``CallbackTrigger``) with a deprecation warning.
    """
    from airflow._shared.module_loading import import_string
    from airflow.utils.deprecation_tools import DeprecatedImportWarning

    with pytest.warns(DeprecatedImportWarning, match="airflow.triggers.callback.CallbackTrigger"):
        resolved = import_string("airflow.triggers.deadline.DeadlineCallbackTrigger")

    assert resolved is CallbackTrigger
