TEST_TASK_ID = "test_task"
TEST_TASK_STATE = None
TEST_RUN_ID = "test_run"
TEST_LOG_URL = "http://localhost:8080/log-url"

# Jinja template patterns
DAG_ID_TEMPLATE_STRING = "{{dag.dag_id}}"
        content = mock_smtphook_hook.return_value.__enter__().send_email_smtp.call_args.kwargs["html_content"]
        assert f"{TRY_NUMBER} of 1" in content

    @pytest.mark.parametrize(
        ("mark_success_url", "row_rendered"),
        [
            pytest.param(TEST_LOG_URL, False, id="alias-of-log-url"),
            pytest.param("http://localhost:8080/confirm?state=success", True, id="dedicated-url"),
        ],
    )
    @mock.patch("airflow.providers.smtp.notifications.smtp.SmtpHook")
    def test_notifier_renders_mark_success_row_only_when_url_differs(
        self,
        mock_smtphook_hook,
        mark_success_url,
        row_rendered,
        create_dag_without_db,
        mock_task_instance,
    ):
        mock_ti = mock_task_instance(
            dag_id=TEST_DAG_ID,
            task_id=TEST_TASK_ID,
            run_id=TEST_RUN_ID,
            try_number=TRY_NUMBER,
            max_tries=0,
            state=TEST_TASK_STATE,
        )
        mock_ti.log_url = TEST_LOG_URL
        mock_ti.mark_success_url = mark_success_url

        notifier = SmtpNotifier(from_email=TEST_SENDER, to=TEST_RECEIVER)
        mock_smtphook_hook.return_value.__enter__.return_value.subject_template = None
        mock_smtphook_hook.return_value.__enter__.return_value.html_content_template = None

        notifier({"dag": create_dag_without_db(TEST_DAG_ID), "ti": mock_ti})

        content = mock_smtphook_hook.return_value.__enter__().send_email_smtp.call_args.kwargs["html_content"]
        assert ("Mark Success Link:" in content) is row_rendered

    @mock.patch("airflow.providers.smtp.notifications.smtp.SmtpHook")
    def test_notifier_with_nondefault_connection_extra(
        self, mock_smtphook_hook, create_dag_without_db, mock_task_instance
