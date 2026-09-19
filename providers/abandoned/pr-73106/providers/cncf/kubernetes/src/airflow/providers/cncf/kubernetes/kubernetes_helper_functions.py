    return isinstance(exc, TRANSIENT_CONNECTION_ERRORS)


# A pod can 404 transiently while it is starting: e.g. it gets preempted by a
# higher-priority daemonset pod scheduled on the same (often newly created) node
# and Kubernetes recreates it elsewhere. Reading pod status should tolerate that
# briefly instead of failing the task outright, unlike other pod API calls (a 404
# on delete or exec is generally not transient), so this is intentionally not part
# of TRANSIENT_STATUS_CODES / _should_retry_api.
POD_READ_TRANSIENT_STATUS_CODES = TRANSIENT_STATUS_CODES | {404}


def _should_retry_pod_read(exc: BaseException) -> bool:
    """Like ``_should_retry_api``, but also retries a transient 404 on pod reads."""
    if isinstance(exc, (SyncApiException, AsyncApiException)):
        return exc.status in POD_READ_TRANSIENT_STATUS_CODES
    return isinstance(exc, TRANSIENT_CONNECTION_ERRORS)


class WaitRetryAfterOrExponential(tenacity.wait.wait_base):
    """Wait strategy that honors Retry-After header on 429, else falls back to exponential backoff."""

    )(func)


def pod_read_retry(func):
    """
    Retry pod-status reads, additionally tolerating a transient 404.

    - Retries the same transient status codes as ``generic_api_retry``, plus 404.
    - Honors Retry-After on 429.
    """
    return tenacity.retry(
        stop=tenacity.stop_after_attempt(API_RETRIES),
        wait=WaitRetryAfterOrExponential(),
        retry=tenacity.retry_if_exception(_should_retry_pod_read),
        reraise=True,
        before_sleep=tenacity.before_sleep_log(log, logging.WARNING),
    )(func)


def rand_str(num):
    """
    Generate random lowercase alphanumeric string of length num.
