            },
        }

    def test_should_not_set_deprecated_branch_and_rev_when_only_ref_is_set(self):
        """A ``ref`` alone must not be silently overridden by the chart's own default branch/rev.

        git-sync v4 gives the legacy ``GIT_SYNC_BRANCH``/``GIT_SYNC_REV`` env vars precedence over
        ``GITSYNC_REF`` whenever both are set (#42918), so the chart must omit them unless the user
        opts into them explicitly.
        """
        docs = render_chart(
            values={
                "executor": "LocalExecutor",  # needed to have git sync added to the scheduler
                "dags": {"gitSync": {"enabled": True, "ref": "v1.2.3"}},
            },
            show_only=["templates/scheduler/scheduler-deployment.yaml"],
        )

        env = jmespath.search("spec.template.spec.containers[1].env", docs[0])
        assert {"name": "GITSYNC_REF", "value": "v1.2.3"} in env
        assert "GIT_SYNC_BRANCH" not in [e["name"] for e in env]
        assert "GIT_SYNC_REV" not in [e["name"] for e in env]

    def test_validate_if_ssh_params_are_added(self):
        docs = render_chart(
            values={
