
    @property
    def mark_success_url(self) -> str:
        """Alias of ``log_url``."""
        # Airflow 3 has no mark-success endpoint to link to.
        return self.log_url


            "Exception:<br>{{exception_html}}<br>"
            'Log: <a href="{{ti.log_url}}">Link</a><br>'
            "Host: {{ti.hostname}}<br>"
        )

    # Add exception_html to context for template rendering
