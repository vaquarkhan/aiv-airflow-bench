import sys
from pathlib import Path

import httpx2
from datamodel_code_generator import (
    DataModelType,
    DatetimeClassType,
    app = InProcessExecutionAPI()

    latest_version = app.app.versions.version_values[0]
    client = httpx2.Client(transport=app.transport)
    openapi_schema = (
        client.get(f"http://localhost/openapi.json?version={latest_version}").raise_for_status().text
    )
