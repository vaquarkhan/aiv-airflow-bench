    assert ids == [triggers[0].id, triggers[1].id, triggers[2].id]


@pytest.mark.parametrize(
    ("triggerer_id", "selected"),
    [
        pytest.param(None, True, id="unassigned"),
        pytest.param(999, True, id="dead_triggerer"),
        pytest.param(100, False, id="alive_triggerer"),
    ],
)
def test_callback_trigger_assignment_respects_alive_triggerers(session, triggerer_id, selected):
    """Callback triggers are only returned when no living triggerer already owns them."""
    trigger = Trigger(classpath="some.trigger", kwargs={})
    trigger.triggerer_id = triggerer_id
    session.add(trigger)
    session.flush()
    callback = TriggererCallback(callback_def=AsyncCallback("classpath.callback"))
    callback.trigger = trigger
    session.add(callback)
    session.flush()

    result = Trigger.get_sorted_triggers(
        capacity=10,
        alive_triggerer_ids=[100, 200],
        queues=None,
        session=session,
    )
    ids = [row[0] for row in result]

    assert (trigger.id in ids) is selected


@pytest.mark.need_serialized_dag
@conf_vars({("core", "multi_team"): "True"})
@pytest.mark.parametrize(
