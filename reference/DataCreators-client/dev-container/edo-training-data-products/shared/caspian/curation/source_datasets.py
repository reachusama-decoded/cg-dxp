import logging
import typing

from caspian.curation import exceptions, miscutils, checkpoints, auditing
from caspian.curation.checkpoints import Checkpoint
from caspian.curation.constants import DatasetLoadCatchupStrategy
from caspian.curation.spark import spark_sql_catalog
from caspian.curation.spark.spark_helpers import PartitionKey, sql_quote, escape_sql_literal

"""This modules provide general functionality how to load the data from standard zone tables."""

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@checkpoints.memorize_checkpoint
def filter_partitions(database: str, table: str,
                      checkpoint: Checkpoint,
                      catchup_strategy: DatasetLoadCatchupStrategy,
                      sql_exec=None,
                      table_partition=None) -> typing.List[PartitionKey]:
    # Retrieve all partitions from the catalog
    all_partitions = spark_sql_catalog.show_partitions(database, table, sql_exec=sql_exec)
    logger.debug(f"All Partitions initial: {all_partitions}")

    # If selected_partitions is provided, filter the partitions
    if table_partition is not None:
        partitions = [p for p in all_partitions if str(p) in table_partition]
        logger.info(f"Filtered Partitions: {partitions}")
        ret = miscutils.coerce_as_list(partitions) or []
        return ret
    else:
        partitions = all_partitions
        logger.debug(f"All Partitions: {partitions}")
    key_builder = spark_sql_catalog.partition_key_builder(database, table, sql_exec)

    lower_or_overrides = checkpoint.as_partition_keys(key_builder)

    x = set(lower_or_overrides) - set(partitions)
    if len(x) != len(lower_or_overrides):
        missing = set(lower_or_overrides) - x
        msg = f"Checkpoint Overrides seems invalid. Please re-check value of overrides: '{missing}'"
        raise exceptions.IllegalStateException(msg)

    if checkpoint.overridden_mode:
        candidates = lower_or_overrides
    else:
        lower = lower_or_overrides[0] if lower_or_overrides else None
        if catchup_strategy == DatasetLoadCatchupStrategy.combined:
            if lower:
                candidates = [c for c in partitions if c > lower]
            else:
                # Do we need to add limit here; for e.g. if more than 10 unprocessed
                # partitions are there, we may not want to process them all together
                # as it may blow-up spark memory
                candidates = partitions
        elif catchup_strategy == DatasetLoadCatchupStrategy.latest:
            if lower:
                candidates = [c for c in partitions if c > lower][-1]
            else:
                candidates = partitions[-1]
        elif catchup_strategy == DatasetLoadCatchupStrategy.chronological:
            if lower:
                candidates = miscutils.first_or_none([c for c in partitions if c > lower])
            else:
                candidates = miscutils.first_or_none(partitions)
        else:
            raise exceptions.UnsupportedOperationException(f"'{catchup_strategy}' is not supported")

    ret = miscutils.coerce_as_list(candidates) or []
    # TODO - implement a common mechanism to check skip using providers.CurrentPipelineMetricsStatusProvider.get()
    return ret


def sql_filter_clause(candidates: typing.List[PartitionKey]) -> str:
    size = len(candidates)
    if size == 0:
        # IF empty list
        filter_sql = "1 = 2"
    elif len(candidates[0].keys) == 1:
        # Single column partition
        filter_sql = f"{sql_quote(candidates[0].keys[0])} IN ( "
        filter_sql += ",".join([f"{escape_sql_literal(p.values[0])}" for p in candidates])
        filter_sql += ")"
    else:
        # Struct Style IN Filter Expression
        filter_sql = f"({', '.join([sql_quote(k) for k in candidates[0].keys])}) IN ("
        filter_sql += ",".join([
            f"( {','.join(escape_sql_literal(v) for v in p.values)})" for p in candidates
        ])
        filter_sql += ")"

    return filter_sql


def get_audit_columns(col_list, run_id) -> str:
    audits = auditing.match_standard_audit_columns(col_list, run_id)
    audit_columns = auditing.generate_audit_columns_for_dbt(audits)

    return audit_columns