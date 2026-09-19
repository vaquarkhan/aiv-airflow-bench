            ]
        )

    def test_read_pod_retries_on_transient_404(self):
        """A pod preempted (e.g. by a daemonset on a new node) can 404 briefly; retry instead of failing."""
        mock.sentinel.metadata = mock.MagicMock()
        self.mock_kube_client.read_namespaced_pod.side_effect = [
            ApiException(status=404),
            mock.sentinel.pod_info,
        ]
        pod_info = self.pod_manager.read_pod(mock.sentinel)
        assert mock.sentinel.pod_info == pod_info
        self.mock_kube_client.read_namespaced_pod.assert_has_calls(
            [
                mock.call(mock.sentinel.metadata.name, mock.sentinel.metadata.namespace),
                mock.call(mock.sentinel.metadata.name, mock.sentinel.metadata.namespace),
            ]
        )

    def test_monitor_pod_empty_logs(self):
        mock.sentinel.metadata = mock.MagicMock()
        running_status = mock.MagicMock()
