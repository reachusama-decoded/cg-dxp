import functools
import typing
import logging
from functools import lru_cache

from caspian.curation import miscutils, exceptions
from caspian.curation.spark.spark_helpers import sql_text_safe_fqn, PartitionKey, GeneralPartitionKeyBuilder

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@functools.lru_cache(64)
def desc_table(db: str, tbl: str, sql_exec=None):
    return sql_exec(f"DESCRIBE TABLE {sql_text_safe_fqn(db, tbl)}")


def get_table_partition_by_columns(database: str, table: str, sql_exec=None) -> typing.List[str]:
    info = desc_table(database, table, sql_exec)
    index = miscutils.find_first_index(info, lambda item: item[0] == "# col_name")
    if index < 0:
        return []

    return [column for column, _, _ in info[index + 1:]]


def get_table_partitions_by_columns(database: str, table: str, sql_exec=None) -> typing.List[str]:
    info_df = sql_exec(f"DESCRIBE DETAIL {sql_text_safe_fqn(database, table)}")
    logger.info(f"Content of info_df:{info_df}")

    # Extract the partition columns from the appropriate field
    if info_df and isinstance(info_df, list):
        # Assuming the partition columns are in the 7th field of the first tuple
        partition_columns_str = info_df[0][7]  # Index 7 corresponds to the partition columns
        if partition_columns_str:
            # Parse the string to extract column names
            part_col = partition_columns_str.strip("[]").replace("'", "").split()
        else:
            part_col = []
    else:
        part_col = []
    logger.info(f"partition columns: {part_col}")

    return part_col


def is_partitioned_table(database: str, table: str, sql_exec=None):
    keys = get_table_partition_by_columns(database, table, sql_exec)
    return len(keys) > 0


def support_merge_into(database: str, table: str, sql_exec=None):
    # We need to examine the table provider.
    # Only DELTA format table provides the MERGE INTO support at the moment
    info = sql_exec(f"DESCRIBE EXTENDED {sql_text_safe_fqn(database, table)}")
    index = miscutils.find_first_index(info, lambda item: item[0] == "# Detailed Table Information")
    if index < 0:
        return False
    provider_index = miscutils.find_first_index(info[index:], lambda item: item[0] == "Provider")
    if provider_index < 0:
        return False

    return info[index + provider_index][1] == "delta"


@lru_cache(5)
def partition_key_builder(database: str, table: str, sql_exec=None):
    table_desc = desc_table(database, table, sql_exec)
    index = miscutils.find_first_index(table_desc, lambda item: item[0] == "# col_name")
    if index <= 0:
        msg = f"Partition key builder cannot be created for non-partitioned table: {database}.{table}"
        raise exceptions.UnsupportedOperationException(msg)

    def type_caster(_dt: str) -> typing.Callable:
        return {
            "string": str,
            "int": int,
            "bigint": int,
            "date": miscutils.try_to_date

        }.get(_dt, lambda v: v)

    meta = {column: {"data_type": dt, "caster": type_caster(dt)} for column, dt, comment in table_desc[index + 1:]}
    return GeneralPartitionKeyBuilder(meta)


def show_partitions(database: str, table: str, sort: bool = True, sql_exec=None) -> typing.List[PartitionKey]:
    """
    Retrieves partition information for a table. Supports both orchestrator-provided partitions
    and data-driven partition discovery.

    Args:
        database (str): The database name.
        table (str): The table name.
        sort (bool): Whether to sort the partitions.
        sql_exec (callable): Function to execute SQL queries.

    Returns:
        List[PartitionKey]: List of partition keys.
    """
    builder = partition_key_builder(database, table, sql_exec)

    # Fallback to querying the data for partitions
    partition_columns = get_table_partitions_by_columns(database, table, sql_exec)
    logger.info(f"table partition columns: {partition_columns}")
    if not partition_columns:
        return []

    # Query to retrieve partition data
    query = f"SELECT {', '.join(partition_columns)} FROM {sql_text_safe_fqn(database, table)} GROUP BY {', '.join(partition_columns)}"
    partition_data = sql_exec(query)
    logger.debug(f"partition data: {partition_data}")

    # Map tuple values to column names
    partitions = [
        builder.parse('/'.join(f"{col}={row[idx]}" for idx, col in enumerate(partition_columns)))
        for row in partition_data
    ]

    if sort:
        partitions.sort()
    logger.debug(f"sorted partitions: {partitions}")

    return partitions


def get_table_columns(database: str, table: str, sql_exec=None) -> str:
    info = desc_table(database, table, sql_exec)
    cols = [item for item in info if item[0] is not None]

    index = miscutils.find_first_index(cols, lambda item: item[0].startswith("#"))
    if index < 0:
        b = []
    else:
        b = [column[0] for column in info[:index]]
    return ','.join(b)
