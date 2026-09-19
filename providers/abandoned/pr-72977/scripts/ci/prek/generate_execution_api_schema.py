os.environ["_AIRFLOW__AS_LIBRARY"] = "1"
sys.path.insert(0, str(Path("airflow-core/src").resolve()))

import httpx2

from airflow.api_fastapi.execution_api.app import InProcessExecutionAPI

app = InProcessExecutionAPI()
version = app.app.versions.version_values[0]
client = httpx2.Client(transport=app.transport)
response = client.get(f"http://localhost/openapi.json?version={version}")
response.raise_for_status()
print(json.dumps(response.json()))
