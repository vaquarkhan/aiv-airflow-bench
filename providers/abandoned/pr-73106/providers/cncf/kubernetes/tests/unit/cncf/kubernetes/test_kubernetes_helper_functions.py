    KubernetesApiException,
    WaitRetryAfterOrExponential,
    _should_retry_api,
    _should_retry_pod_read,
    create_unique_id,
)

    assert not _should_retry_api(exc)


def test_should_retry_pod_read():
    exc = HTTPError()
    assert _should_retry_pod_read(exc)

    exc = KubernetesApiException()
    assert _should_retry_pod_read(exc)

    exc = SyncApiException(status=500)
    assert _should_retry_pod_read(exc)

    exc = AsyncApiException(status=500)
    assert _should_retry_pod_read(exc)

    exc = SyncApiException(status=404)
    assert _should_retry_pod_read(exc)

    exc = AsyncApiException(status=404)
    assert _should_retry_pod_read(exc)

    exc = SyncApiException(status=400)
    assert not _should_retry_pod_read(exc)


class TestWaitRetryAfterOrExponential:
    @pytest.mark.no_wait_patch_disabled
    @pytest.mark.parametrize(("exception"), [SyncApiException, AsyncApiException])
