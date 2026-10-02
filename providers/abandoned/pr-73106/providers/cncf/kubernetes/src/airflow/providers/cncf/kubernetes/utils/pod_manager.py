    KubernetesApiException,
    PodLaunchFailedException,
    generic_api_retry,
    pod_read_retry,
)
from airflow.providers.cncf.kubernetes.utils.container import (
    container_is_completed,
        except HTTPError as e:
            raise KubernetesApiException(f"There was an error reading the kubernetes API: {e}")

    @pod_read_retry
    def read_pod(self, pod: V1Pod) -> V1Pod:
        """Read POD information."""
        try:
