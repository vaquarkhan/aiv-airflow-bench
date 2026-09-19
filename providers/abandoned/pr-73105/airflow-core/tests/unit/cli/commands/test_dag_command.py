        )
        dag_command.dag_list_jobs(args)

    @pytest.mark.parametrize("limit", ["abc", "-1", "0"])
    def test_cli_list_jobs_with_invalid_limit(self, limit):
        with pytest.raises(SystemExit) as exc_info:
            self.parser.parse_args(["dags", "list-jobs", "--limit", limit])
        assert exc_info.value.code == 2

    def test_pause(self):
        args = self.parser.parse_args(["dags", "pause", "example_bash_operator"])
        dag_command.dag_pause(args)
