from unittest import mock
from uuid import UUID

import httpx2
import pytest
from fastapi import Request, status
from fastapi.params import Security as SecurityParam
def test_in_process_execution_api_runs_without_jwt_secret():
    """The in-process API must not require ``api_auth/jwt_secret`` to be configured."""
    api = InProcessExecutionAPI()
    with httpx2.Client(transport=api.transport) as client:
        response = client.get("http://localhost/health")
    assert response.status_code == 200

