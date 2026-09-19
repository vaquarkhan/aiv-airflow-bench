
    @property
    def mark_success_url(self) -> str:
        """Alias of ``log_url``."""
        # Airflow 3 has no mark-success endpoint to link to.
        return self.log_url

    @provide_session
