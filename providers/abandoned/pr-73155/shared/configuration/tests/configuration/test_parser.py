
        assert test_conf.getjson("test", "json", fallback=fallback) == fallback

    def test_getjson_from_file(self, tmp_path):
        """Test AirflowConfigParser.getjson loading from a file path via key_file"""
        json_file = tmp_path / "config.json"
        json_file.write_text('{"key": "value", "items": [1, 2, 3]}')

        config = textwrap.dedent(
            f"""
            [test]
            data_file = {json_file}
            """
        )
        test_conf = AirflowConfigParser()
        test_conf.read_string(config)

        assert test_conf.getjson("test", "data") == {"key": "value", "items": [1, 2, 3]}

    def test_getjson_from_file_env_var(self, tmp_path, monkeypatch):
        """Test AirflowConfigParser.getjson loading from a file path via environment variable"""
        json_file = tmp_path / "env_config.json"
        json_file.write_text('{"env_key": "env_value"}')

        monkeypatch.setenv("AIRFLOW__TEST__ENV_DATA_FILE", str(json_file))
        test_conf = AirflowConfigParser()

        assert test_conf.getjson("test", "env_data") == {"env_key": "env_value"}

    def test_getjson_from_file_invalid_json(self, tmp_path):
        """Test AirflowConfigParser.getjson raising AirflowConfigException on invalid json file"""
        json_file = tmp_path / "invalid.json"
        json_file.write_text("invalid json content")

        config = textwrap.dedent(
            f"""
            [test]
            bad_data_file = {json_file}
            """
        )
        test_conf = AirflowConfigParser()
        test_conf.read_string(config)

        with pytest.raises(AirflowConfigException, match="Unable to load json from file"):
            test_conf.getjson("test", "bad_data")

    def test_has_option(self):
        """Test AirflowConfigParser.has_option"""
        test_config = """[test]
