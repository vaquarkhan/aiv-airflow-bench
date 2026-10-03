        :param timeout: Optional. The amount of time, in seconds, to wait for the request to complete.
            Note that if `retry` is specified, the timeout applies to each individual attempt.
        """
        if isinstance(table_resource, TableReference):
            _table_resource: dict[str, Any] = {"tableReference": table_resource.to_api_repr()}
        elif hasattr(table_resource, "to_api_repr"):
            _table_resource = table_resource.to_api_repr()
        elif isinstance(table_resource, dict):
            _table_resource = dict(table_resource)
            if isinstance(_table_resource.get("tableReference"), TableReference):
                _table_resource["tableReference"] = _table_resource["tableReference"].to_api_repr()
        else:
            raise TypeError(f"Invalid table_resource type: {type(table_resource)}")

        if schema_fields:
            _table_resource["schema"] = {"fields": schema_fields}

        table_resource_final = self._resolve_table_reference(
            table_resource=_table_resource,
            project_id=project_id,
            dataset_id=dataset_id,
            table_id=table_id,
        )
        table = Table.from_api_repr(table_resource_final)
        result = self.get_client(project_id=project_id, location=location).create_table(
            table=table, exists_ok=exists_ok, retry=retry, timeout=timeout
        )
