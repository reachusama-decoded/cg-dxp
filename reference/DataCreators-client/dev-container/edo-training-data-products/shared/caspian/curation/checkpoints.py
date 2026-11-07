import functools
import logging
import os

from caspian.curation import miscutils, exceptions
from caspian.curation.constants import GenericSQLExecWithTupleResults
from caspian.curation.spark.spark_helpers import escape_sql_literal, PartitionKey, get_table_location

"""This modules provide a CHECKPOINT functionality to store the checkpoint in a hive table.
  The hive table can be an external or managed table and is subjected to deployment strategy.
      For  backing table DDL, please see caspian/curation/state/checkpoints.sql

  This class also support the manual override of checkpoint to support the re-processing of already processed
  data. Currently, it is capable to detect it was running in overridden mode and will automatically clear out the
  overridden checkpoint value to resume the normal processing next time.
"""

_log = logging.getLogger(__name__)


class Checkpoint:
    # # BEFORE (resolved once at import time):
    # TABLE_NAME = f"{os.environ.get('CSPN_SYS_DB_NAME','cspn_sys')}.standard_dataset_checkpoints"
    # AFTER — resolved lazily each time it is accessed,
    # so CSPN_SYS_DB_NAME set before the first SQL call takes effect.
    _TABLE_NAME_OVERRIDE: str = None  # set via Checkpoint.override_table_name()

    @classmethod
    def get_table_name(cls) -> str:
        if cls._TABLE_NAME_OVERRIDE:
            return cls._TABLE_NAME_OVERRIDE
        schema = os.environ.get('CSPN_SYS_DB_NAME', 'cspn_sys')
        return f"{schema}.standard_dataset_checkpoints"

    @classmethod
    def override_table_name(cls, schema_or_table: str) -> None:
        """Call this at process start to redirect all checkpoint reads/writes.

        Accepts either:
        - schema/catalog.schema (e.g. jsum, caspian_ig_dev.jsum)
        - full table name (e.g. jsum.standard_dataset_checkpoints)
        """
        if schema_or_table and schema_or_table.endswith('.standard_dataset_checkpoints'):
            cls._TABLE_NAME_OVERRIDE = schema_or_table
        else:
            cls._TABLE_NAME_OVERRIDE = f"{schema_or_table}.standard_dataset_checkpoints"
        _log.info(f"Checkpoint table overridden to: {cls._TABLE_NAME_OVERRIDE}")

    # , ds: str, pipeline: str = "all", app_name: str = "unspecified"):
    def __init__(self, app_name: str, pipeline: str, ds: str, value: str = None, overridden_mode: bool = False):
        self.app_name = app_name
        self.pipeline = pipeline
        self.ds = ds
        self.value = value
        self.overridden_mode = overridden_mode
        self.to_be_confirm = None

    def __str__(self):
        return f"{self.__dict__}"

    @property
    def key(self):
        return f"{self.app_name}.{self.pipeline}.{self.ds}"

    def as_partition_keys(self, key_builder):
        p = []
        if self.overridden_mode:
            for v in miscutils.split_csv_line(self.value):
                p.append(key_builder.parse(v))
        else:
            if self.value:
                p.append(key_builder.parse(self.value))
        return p

    def __hash__(self):
        return hash(self.key)

    def __eq__(self, other):
        return self.key == other.key


def read_checkpoint(exec_sql: GenericSQLExecWithTupleResults,
                    app_name: str,
                    pipeline: str,
                    ds: str) -> Checkpoint:
    _log.info(f"Checkpoint table: {Checkpoint.get_table_name()}")
    _log.info(f"Checkpoint lookup app_name={app_name}, pipeline={pipeline}, ds={ds}")
    sql = (f"SELECT value_override, value, value_override_notes FROM {Checkpoint.get_table_name()}"
           f" WHERE app_name = {escape_sql_literal(app_name)}"
           f"  AND  ds = {escape_sql_literal(ds)}"
           f"  AND  pipeline = {escape_sql_literal(pipeline)}"
           )
    _log.info(f"Checkpoint SQL: {sql}")
    found = miscutils.first_or_none(exec_sql(sql))
    value_override, value, value_override_notes = found if found else ("", "", "")

    debug_string = ""
    if value_override:
        overridden_mode = True
        checkpoint = value_override
        debug_string = f"(Overridden Mode - {value_override_notes})"
    else:
        checkpoint = value
        overridden_mode = False

    _log.info(f"Found checkpoint: {pipeline}.{ds}: {checkpoint} {debug_string}")

    return Checkpoint(app_name, pipeline, ds, checkpoint, overridden_mode)


def write_checkpoint_delta_merge(exec_sql: GenericSQLExecWithTupleResults, data: Checkpoint,
                                 new_value: str = None) -> None:
    # remove all sql quotes to creating sql path
    target_value = new_value or data.value
    location = get_table_location(exec_sql, Checkpoint.get_table_name())
    _log.info(f"Resetting overridden checkpoint using delta merge statement. Next time it will be resume from original"
              f" checkpoint.{data}. Checkpoint value is ignored: {data.value}")
    exec_sql(f"""with temp_tab(value, sys_update_ts,value_override,value_override_notes,app_name,pipeline,ds ) 
    as  (select '{target_value}', current_timestamp(), '', '',{escape_sql_literal(data.app_name)},
    {escape_sql_literal(data.pipeline)},{escape_sql_literal(data.ds)})
MERGE INTO {Checkpoint.get_table_name()} AS target
USING temp_tab as source
on target.app_name = source.app_name and target.pipeline = source.pipeline and target.ds == source.ds
WHEN MATCHED THEN
    UPDATE SET target.value = '{target_value}', sys_update_ts=current_timestamp()
WHEN NOT MATCHED THEN
    INSERT *""")
    _log.info("Checkpoint written Successfully.")


def write_checkpoint(exec_sql: GenericSQLExecWithTupleResults, data: Checkpoint, new_value: str = None) -> None:
    target_value = escape_sql_literal(new_value or data.value)
    sql = (f"INSERT OVERWRITE TABLE {Checkpoint.get_table_name()} PARTITION"
           f" (app_name={escape_sql_literal(data.app_name)}"
           f", pipeline={escape_sql_literal(data.pipeline)}"
           f", ds={escape_sql_literal(data.ds)} )"
           f" SELECT {target_value}, CURRENT_TIMESTAMP, NULL, NULL"
           )

    if data.overridden_mode:
        sql = (f"INSERT OVERWRITE TABLE {Checkpoint.get_table_name()} PARTITION"
               f" (app_name={escape_sql_literal(data.app_name)}"
               f", pipeline={escape_sql_literal(data.pipeline)}"
               f", ds={escape_sql_literal(data.ds)}) "
               f" SELECT {target_value}, sys_update_ts , NULL, NULL "
               f" FROM {Checkpoint.get_table_name()} "
               f" WHERE app_name={escape_sql_literal(data.app_name)} "
               f" AND pipeline={escape_sql_literal(data.pipeline)} "
               f" AND ds={escape_sql_literal(data.ds)}"
               )

        _log.info(f"Resetting overridden checkpoint. Next time it will be resume from original"
                  f" checkpoint.{data}. Checkpoint value is ignored: {data.value}")

    _log.debug(f"Overwriting checkpoint: {sql}")
    last_e = None
    for retry in range(0, 5):
        try:
            exec_sql(sql)
            return
        except Exception as e:  # noqa It can either be py4j.Exception or pyodbc Exception
            last_e = e
    _log.error(f"Commit to checkpoint failed. SQL was: {sql} . We may need to update the checkpoint manually")
    raise last_e


class CheckpointMemoryStore:
    _cache = {}

    @classmethod
    def update(cls, checkpoint, new_value):
        cls._cache[checkpoint] = new_value

    @classmethod
    def items(cls):
        return cls._cache.items()

    @classmethod
    def get_value(cls, checkpoint):
        return cls._cache.get(checkpoint)


def memorize_checkpoint(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        checkpoint = miscutils.find_first_item(list(args),
                                               lambda c: isinstance(c, Checkpoint)) or kwargs.get("checkpoint")

        if checkpoint is None:
            msg = f"You cannot decorate function: '{fn.__name__} with memorize_checkpoint"
            raise exceptions.IllegalStateException(msg)

        keys = fn(*args, **kwargs)
        new_value = miscutils.last_or_none(keys)

        memorize_checkpoint_value(checkpoint, new_value)

        return keys

    return wrapper


def memorize_checkpoint_value(checkpoint: Checkpoint, new_value: PartitionKey):
    if new_value is not None:
        CheckpointMemoryStore.update(checkpoint, str(new_value))


if miscutils.to_bool(os.getenv("USE_WRITE_CHECKPOINT_MERGE", "yes")):
    write_checkpoint = write_checkpoint_delta_merge  # noqa F811
else:
    _log.warning("Going to use write checkpoint using legacy method. Please consider USE_WRITE_CHECKPOINT_PYARROW=yes")
