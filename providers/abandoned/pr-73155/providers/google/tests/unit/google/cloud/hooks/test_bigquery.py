            timeout=None,
        )

    @mock.patch("airflow.providers.google.cloud.hooks.bigquery.Client")
    def test_create_table_with_table_object(self, mock_bq_client):
        table_ref = TableReference.from_string(f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}")
        real_table = Table(table_ref)
        self.hook.create_table(
            project_id=PROJECT_ID, dataset_id=DATASET_ID, table_id=TABLE_ID, table_resource=real_table
        )
        assert mock_bq_client.return_value.create_table.called
        call_args = mock_bq_client.return_value.create_table.call_args[1]
        assert call_args["table"].project == PROJECT_ID
        assert call_args["table"].dataset_id == DATASET_ID
        assert call_args["table"].table_id == TABLE_ID

    @mock.patch("airflow.providers.google.cloud.hooks.bigquery.Client")
    def test_create_table_with_table_reference(self, mock_bq_client):
        table_ref = TableReference.from_string(f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}")
        self.hook.create_table(
            project_id=PROJECT_ID, dataset_id=DATASET_ID, table_id=TABLE_ID, table_resource=table_ref
        )
        assert mock_bq_client.return_value.create_table.called
        call_args = mock_bq_client.return_value.create_table.call_args[1]
        assert call_args["table"].project == PROJECT_ID
        assert call_args["table"].dataset_id == DATASET_ID
        assert call_args["table"].table_id == TABLE_ID

    @mock.patch("airflow.providers.google.cloud.hooks.bigquery.Table.from_api_repr")
    @mock.patch("airflow.providers.google.cloud.hooks.bigquery.Client")
    @pytest.mark.parametrize(
