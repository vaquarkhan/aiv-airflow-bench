from types import SimpleNamespace
from typing import TYPE_CHECKING, Any

from sqlalchemy import and_, column, func, inspect, literal, literal_column, or_, select, table, text
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import aliased
from airflow.cli.simple_table import AirflowConsole
from airflow.configuration import conf
from airflow.exceptions import AirflowException
from airflow.models.callback import TERMINAL_STATES
from airflow.utils.db import reflect_tables
from airflow.utils.helpers import ask_yesno
from airflow.utils.session import NEW_SESSION, provide_session
from airflow.utils.state import CallbackState
from airflow.utils.types import DagRunType

if TYPE_CHECKING:
logger = logging.getLogger(__name__)

ARCHIVE_TABLE_PREFIX = "_airflow_deleted__"
# Alias _build_query gives the table being cleaned; a correlated extra_filter refers to it by name.
_BASE_TABLE_ALIAS = "base"
# Archived tables created by DB migrations
ARCHIVED_TABLES_FROM_DB_MIGRATIONS = [
    "_xcom_archive"  # Table created by the AF 2 -> 3.0.0 migration when the XComs had pickled values
        dependent_tables=["task_instance", "task_state_store", "deadline"],
    ),
    _TableConfig(table_name="asset_event", recency_column_name="timestamp", dag_id_column_name="dag_id"),
    # Carries no foreign key, so rows are left behind when the partition Dag run they describe
    # is cascade-deleted with its dag_run. Only such orphans may be purged: rows whose partition
    # Dag run still exists are the evidence the scheduler evaluates to decide when that pending
    # run fires, so age alone must not delete them.
    _TableConfig(
        table_name="partitioned_asset_key_log",
        recency_column_name="created_at",
        extra_columns=["asset_partition_dag_run_id"],
        extra_filters=[
            column("asset_partition_dag_run_id").not_in(
                select(column("id")).select_from(table("asset_partition_dag_run"))
            )
        ],
    ),
    _TableConfig(table_name="import_error", recency_column_name="timestamp"),
    _TableConfig(table_name="log", recency_column_name="dttm", dag_id_column_name="dag_id"),
    _TableConfig(
        table_name="task_instance",
        recency_column_name="start_date",
    _TableConfig(table_name="task_reschedule", recency_column_name="start_date", dag_id_column_name="dag_id"),
    _TableConfig(table_name="xcom", recency_column_name="timestamp", dag_id_column_name="dag_id"),
    _TableConfig(table_name="_xcom_archive", recency_column_name="timestamp", dag_id_column_name="dag_id"),
    _TableConfig(
        table_name="callback",
        recency_column_name="created_at",
        extra_columns=["id", "state"],
        # Purging a callback cascades to its deadline row, so only finished callbacks are purged;
        # a state this code does not know keeps its rows. An unfired deadline's callback sits in
        # SCHEDULED, which is neither active nor terminal, until the deadline is missed; it is
        # purged only once no deadline references it, as deleting a Dag run cascades away the
        # deadline at the database level and leaves the callback behind. Dag-processor callbacks
        # carry no state and are deleted as they are dispatched.
        extra_filters=[
            or_(
                column("state").in_(sorted(TERMINAL_STATES)),
                column("state").is_(None),
                and_(
                    column("state") == CallbackState.SCHEDULED,
                    ~select(literal(1))
                    .select_from(table("deadline", column("callback_id")))
                    .where(column("callback_id") == literal_column(f"{_BASE_TABLE_ALIAS}.id"))
                    .exists(),
                ),
            )
        ],
        dependent_tables=["deadline"],
    ),
    _TableConfig(table_name="celery_taskmeta", recency_column_name="date_done"),
    _TableConfig(table_name="celery_tasksetmeta", recency_column_name="date_done"),
    _TableConfig(
    referenced_pk_column: str = "id",
    **kwargs,
) -> Select:
    base_table_alias = _BASE_TABLE_ALIAS
    base_table = aliased(orm_model, name=base_table_alias)
    query = select(text(f"{base_table_alias}.*")).select_from(base_table)
    base_table_recency_col = base_table.c[recency_column.name]
