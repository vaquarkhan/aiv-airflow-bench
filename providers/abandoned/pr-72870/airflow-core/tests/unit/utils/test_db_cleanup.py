from contextlib import suppress
from importlib import import_module
from io import StringIO
from unittest.mock import MagicMock, mock_open, patch
from uuid import uuid4

import pendulum
import pytest
from sqlalchemy import Column, Integer, MetaData, Table, func, insert, inspect, literal, select, text
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.ext.declarative import DeclarativeMeta

    _cleanup_table,
    _confirm_drop_archives,
    _dump_table_to_file,
    _effective_table_names,
    _get_archived_table_names,
    _TableConfig,
    config_dict,
        """
        import pkgutil

        import airflow.models

        # Walk the package's own __path__ rather than rebuilding it from this file's
        # location: a path guessed relative to the test resolves to nothing once the
        # sources move, leaving the assertions below with an empty set to check.
        mods = [f"airflow.models.{name}" for _, name, _ in pkgutil.iter_modules(airflow.models.__path__)]

        all_models = {}
        for mod_name in mods:
            "dag_priority_parsing_request",  # Records are purged once per DAG Processing loop, not a
            # significant source of data.
            "dag_bundle",  # leave alone - not appropriate for cleanup
            "team",  # leave alone - team configuration, not run data
            # leave alone - per-asset key/value state, upserted in place (PK is asset_id+key),
            # so it is bounded and current, not accumulating history; removed with its asset
            "asset_state_store",
            # Purged indirectly: each of these hangs off a cleaned table by an
            # ON DELETE CASCADE foreign key, so the rows go when the parent does.
            # cascade from dag_run once the partition run has fired; while it is still
            # pending its created_dag_run_id is NULL, so those rows are not cleaned
            "asset_partition_dag_run",
            "asset_watcher",  # cascade from trigger
            "dag_favorite",  # cascade from dag
            "deadline_alert",  # cascade from serialized_dag, which cascades from dag_version
            "hitl_detail",  # cascade from task_instance
            "hitl_detail_history",  # cascade from task_instance_history
            "task_inlet_asset_reference",  # cascade from dag
        }

        from airflow.utils.db_cleanup import config_dict

        print(f"all_models={set(all_models)}")
        print(f"excl+conf={exclusion_list.union(config_dict)}")
        # Without this the two assertions below hold trivially for an empty set,
        # which is how a table can go unnoticed by this check for several releases.
        assert all_models, "discovered no models, so this check would pass vacuously"
        assert set(all_models) - exclusion_list.union(config_dict) == set()
        assert exclusion_list.isdisjoint(config_dict)

            assert seeded[state] in survivors, f"{state} row should NOT be cleaned up"
        for state in ("success", "failed"):
            assert seeded[state] not in survivors, f"{state} row should be cleaned up"


class TestCallbackCleanupConfig:
    """The callback table is registered under the name it actually has in the schema."""

    def test_callback_is_configured_under_its_current_name(self):
        # The table was renamed from callback_request to callback; a config entry naming a
        # table that does not exist is skipped with a warning, so the rows are never purged.
        assert "callback" in config_dict
        assert "callback_request" not in config_dict

    def test_removed_tables_are_not_configured(self):
        assert "sla_miss" not in config_dict

    def test_cleaning_callback_pulls_in_its_dependent_deadline_rows(self):
        # deadline.callback_id cascades from callback, so deadline has to be cleaned
        # (and archived) first, or those rows would vanish unrecorded.
        selected, _ = _effective_table_names(table_names=["callback"])
        assert selected == ["deadline", "callback"]


@pytest.mark.db_test
class TestCallbackCleanup:
    """Cleanup must purge finished callbacks without disturbing ones that can still run."""

    def setup_method(self):
        from tests_common.test_utils.db import clear_db_callbacks, clear_db_deadline

        clear_db_deadline()
        clear_db_callbacks()
        with create_session() as session:
            for name in _get_archived_table_names(["callback", "deadline"], session):
                session.execute(text(f"DROP TABLE {name}"))
            session.commit()

    def teardown_method(self):
        from tests_common.test_utils.db import clear_db_callbacks, clear_db_deadline

        clear_db_deadline()
        clear_db_callbacks()
        with create_session() as session:
            for name in _get_archived_table_names(["callback", "deadline"], session):
                session.execute(text(f"DROP TABLE {name}"))
            session.commit()

    @staticmethod
    def _add_callback(session, state, created_at):
        from airflow.executors.workloads.callback import CallbackFetchMethod
        from airflow.models.callback import Callback

        callback = Callback(priority_weight=1)
        callback.fetch_method = CallbackFetchMethod.IMPORT_PATH
        callback.state = state
        callback.created_at = created_at
        session.add(callback)
        session.flush()
        return callback.id

    @staticmethod
    def _count_callbacks(session, callback_id):
        from airflow.models.callback import Callback

        return session.scalar(select(func.count()).select_from(Callback).where(Callback.id == callback_id))

    @staticmethod
    def _clean_callbacks(cutoff):
        with create_session() as session:
            _cleanup_table(
                **config_dict["callback"].__dict__,
                clean_before_timestamp=cutoff,
                dry_run=False,
                verbose=False,
                confirm=False,
                skip_archive=True,
                session=session,
            )

    @pytest.mark.parametrize(
        ("state", "should_survive"),
        [
            ("success", False),
            ("failed", False),
            (None, False),
            ("scheduled", False),
            ("pending", True),
            ("queued", True),
            ("running", True),
        ],
        ids=[
            "success",
            "failed",
            "dag-processor-null-state",
            "scheduled-orphan",
            "pending",
            "queued",
            "running",
        ],
    )
    def test_only_finished_callbacks_are_purged(self, state, should_survive):
        old = pendulum.now(tz="UTC").subtract(days=30)
        cutoff = pendulum.now(tz="UTC").subtract(days=1)

        with create_session() as session:
            callback_id = self._add_callback(session, state, old)
            session.commit()

        self._clean_callbacks(cutoff)

        with create_session() as session:
            survived = self._count_callbacks(session, callback_id)

        assert bool(survived) is should_survive

    def test_unfired_deadline_callback_and_its_deadline_survive(self, dag_maker):
        from airflow.models.deadline import Deadline
        from airflow.sdk.definitions.callback import AsyncCallback
        from airflow.utils.state import CallbackState

        old = pendulum.now(tz="UTC").subtract(days=30)
        cutoff = pendulum.now(tz="UTC").subtract(days=1)
        with dag_maker("test_db_clean_unfired_deadline"):
            pass
        dag_run = dag_maker.create_dagrun()

        with create_session() as session:
            deadline = Deadline(
                deadline_time=pendulum.now(tz="UTC").add(days=10),
                callback=AsyncCallback("tests.unit.models.test_deadline.callback_for_deadline"),
                dagrun_id=dag_run.id,
                deadline_alert_id=None,
            )
            session.add(deadline)
            session.flush()
            deadline.callback.created_at = old
            assert deadline.callback.state == CallbackState.SCHEDULED
            deadline_id, callback_id = deadline.id, deadline.callback.id

        self._clean_callbacks(cutoff)

        with create_session() as session:
            assert self._count_callbacks(session, callback_id) == 1
            assert (
                session.scalar(select(func.count()).select_from(Deadline).where(Deadline.id == deadline_id))
                == 1
            )

    def test_recent_finished_callback_is_kept(self):
        recent = pendulum.now(tz="UTC")
        cutoff = pendulum.now(tz="UTC").subtract(days=1)

        with create_session() as session:
            callback_id = self._add_callback(session, "success", recent)
            session.commit()

        self._clean_callbacks(cutoff)

        with create_session() as session:
            assert self._count_callbacks(session, callback_id) == 1

    def test_finished_callbacks_are_archived_not_just_deleted(self):
        """Archiving is the default path, so the purged rows must be recoverable."""
        from airflow.models.callback import Callback

        old = pendulum.now(tz="UTC").subtract(days=30)
        cutoff = pendulum.now(tz="UTC").subtract(days=1)

        with create_session() as session:
            self._add_callback(session, "success", old)
            session.commit()

        with create_session() as session:
            _cleanup_table(
                **config_dict["callback"].__dict__,
                clean_before_timestamp=cutoff,
                dry_run=False,
                verbose=False,
                confirm=False,
                skip_archive=False,
                session=session,
            )

        with create_session() as session:
            archives = _get_archived_table_names(["callback"], session)
            assert archives, "no archive table was created"
            archived = sum(
                session.execute(text(f"SELECT count(*) FROM {name}")).scalar() for name in archives
            )
            assert archived == 1
            assert session.scalar(select(func.count()).select_from(Callback)) == 0

    def test_deadline_of_a_runnable_callback_is_not_cascade_deleted(self):
        """deadline.callback_id is ON DELETE CASCADE, so purging a live callback would drop its deadline."""
        old = pendulum.now(tz="UTC").subtract(days=30)
        cutoff = pendulum.now(tz="UTC").subtract(days=1)
        future = pendulum.now(tz="UTC").add(days=365)

        from airflow.models.deadline import Deadline

        with create_session() as session:
            callback_id = self._add_callback(session, "scheduled", old)
            session.execute(
                insert(Deadline.__table__).values(
                    id=uuid4(),
                    deadline_time=future,
                    callback_id=callback_id,
                    created_at=old,
                    last_updated_at=old,
                    missed=False,
                )
            )
            session.commit()

        self._clean_callbacks(cutoff)

        with create_session() as session:
            assert session.scalar(select(func.count()).select_from(Deadline)) == 1


@pytest.mark.db_test
class TestPartitionedAssetKeyLogCleanup:
    """Only orphaned key-log rows may go: live ones drive pending partition-run evaluation."""

    def setup_method(self):
        with create_session() as session:
            session.execute(text("DELETE FROM partitioned_asset_key_log"))
            session.execute(text("DELETE FROM asset_partition_dag_run"))
            session.commit()

    teardown_method = setup_method

    @staticmethod
    def _add_key_log(session, apdr_id, created_at):
        from airflow.models.asset import PartitionedAssetKeyLog

        row = PartitionedAssetKeyLog(
            asset_id=1,
            asset_event_id=1,
            asset_partition_dag_run_id=apdr_id,
            source_partition_key="2024-01-01",
            target_dag_id="cleanup_probe_dag",
            target_partition_key="2024-01-01",
        )
        row.created_at = created_at
        session.add(row)
        session.flush()
        return row.id

    def test_only_orphaned_key_log_rows_are_purged(self):
        from airflow.models.asset import AssetPartitionDagRun, PartitionedAssetKeyLog

        old = pendulum.now(tz="UTC").subtract(days=30)
        cutoff = pendulum.now(tz="UTC").subtract(days=1)

        with create_session() as session:
            apdr = AssetPartitionDagRun(target_dag_id="cleanup_probe_dag", partition_key="2024-01-01")
            session.add(apdr)
            session.flush()
            ids = {
                "old orphan": self._add_key_log(session, apdr_id=apdr.id + 1000, created_at=old),
                "old but live": self._add_key_log(session, apdr_id=apdr.id, created_at=old),
                "recent orphan": self._add_key_log(
                    session, apdr_id=apdr.id + 1000, created_at=pendulum.now(tz="UTC")
                ),
            }
            session.commit()

        with create_session() as session:
            _cleanup_table(
                **config_dict["partitioned_asset_key_log"].__dict__,
                clean_before_timestamp=cutoff,
                dry_run=False,
                verbose=False,
                confirm=False,
                skip_archive=True,
                session=session,
            )

        with create_session() as session:
            surviving = set(session.scalars(select(PartitionedAssetKeyLog.id)).all())

        assert ids["old orphan"] not in surviving
        assert ids["old but live"] in surviving, "evidence for a pending partition run must not be deleted"
        assert ids["recent orphan"] in surviving, "age filter still applies to orphans"


def _delete_test_timestamp():
    return pendulum.DateTime(2024, 1, 2, 3, 4, 5, tzinfo=pendulum.timezone("UTC"))


def _build_do_delete_test_objects():
    metadata = MetaData()
    source_table = Table("dag_version", metadata, Column("id", Integer, primary_key=True))
    target_table = Table(
        f"{ARCHIVE_TABLE_PREFIX}{source_table.name}__20240102030405",
        metadata,
        Column("id", Integer, primary_key=True),
    )
    query = select(literal(1).label("id"))
    return metadata, source_table, target_table, query


def _create_pinned_dag_version_cleanup_data(*, base_date):
    bundle_name = f"testing-{uuid4()}"
    dag_id = f"test-dag_{uuid4()}"

    with create_session() as session:
        session.add(DagBundleModel(name=bundle_name))
        session.flush()

        dag = DAG(dag_id=dag_id)
        session.add(DagModel(dag_id=dag_id, bundle_name=bundle_name))

        old_dag_version = DagVersion(
            dag_id=dag_id,
            version_number=1,
            bundle_name=bundle_name,
            created_at=base_date,
            last_updated=base_date,
        )
        new_dag_version = DagVersion(
            dag_id=dag_id,
            version_number=2,
            bundle_name=bundle_name,
            created_at=base_date.add(minutes=1),
            last_updated=base_date.add(minutes=1),
        )
        session.add_all([old_dag_version, new_dag_version])
        session.flush()

        dag_run = DagRun(
            dag_id,
            run_id="run-1",
            run_type=DagRunType.MANUAL,
            start_date=base_date,
        )
        task = PythonOperator(task_id="dummy-task", dag=dag, python_callable=print)
        ti = create_task_instance(task, run_id=dag_run.run_id, dag_version_id=old_dag_version.id)
        ti.dag_id = dag_id
        ti.start_date = base_date

        session.add_all([dag_run, ti])
        session.commit()

    return base_date.add(days=1)


def _get_dag_version_archive_table_names(*, session):
    return [
        table_name
        for table_name in _get_archived_table_names(["dag_version"], session)
        if table_name.startswith(f"{ARCHIVE_TABLE_PREFIX}dag_version__")
    ]


def _dag_version_config_without_row_exclusion():
    """Live dag_version cleanup config with row-exclusion filters disabled.

    The backend regression tests above pin ``_do_delete``'s rollback-before-drop
    behaviour, which requires the
    DELETE to actually hit the ``task_instance.dag_version_id`` FK violation.
    The live config may exclude FK-pinned rows from the deletion query (see
    PR #68339), which would turn these tests into no-ops -- so strip any such
    filters from a copy of the config.
    """
    config = dict(config_dict["dag_version"].__dict__)
    for key in ("extra_filters", "skip_if_referenced"):
        if key in config:
            config[key] = None
    return config
