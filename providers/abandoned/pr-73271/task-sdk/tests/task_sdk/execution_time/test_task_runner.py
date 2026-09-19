                    assert kwargs["to"] == emails
                    assert (
                        kwargs["html_content"]
                        == 'Try {{try_number}} out of {{max_tries + 1}}<br>Exception:<br>{{exception_html}}<br>Log: <a href="{{ti.log_url}}">Link</a><br>Host: {{ti.hostname}}<br>'
                    )

    @pytest.mark.parametrize(
                    assert kwargs["to"] == emails
                    assert (
                        kwargs["html_content"]
                        == 'Try {{try_number}} out of {{max_tries + 1}}<br>Exception:<br>{{exception_html}}<br>Log: <a href="{{ti.log_url}}">Link</a><br>Host: {{ti.hostname}}<br>'
                    )

    def test_email_with_custom_templates(self, create_runtime_ti, mock_supervisor_comms, tmp_path):
