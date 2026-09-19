  Exception:<br>{{exception_html}}<br>
  Log: <a href="{{ti.log_url}}">Link</a><br>
  Host: {{ti.hostname}}<br>

``ti.mark_success_url`` is still available for templates carried over from Airflow 2, but it now returns
the same URL as ``ti.log_url`` — Airflow 3 has no dedicated mark-success endpoint, so mark a task
successful from the task instance page that link opens.

.. note::
    For more information on setting the configuration, see :doc:`set-config`
