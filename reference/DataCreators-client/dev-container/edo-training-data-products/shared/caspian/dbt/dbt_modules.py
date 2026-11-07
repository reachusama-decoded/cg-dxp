import functools
import logging
import typing
import uuid
from pathlib import Path
from typing import Dict, Any
from datetime import timedelta

import dbt.context.base as _dbt_base
from dbt.adapters.base import BaseRelation
from dbt.context.providers import RuntimeConfigObject

from caspian.curation import checkpoints, source_datasets, miscutils
from caspian.curation.checkpoints import CheckpointMemoryStore
from caspian.curation.constants import GenericSQLExecWithTupleResults, read_load_type_and_catch_up_strategy
from caspian.curation.miscutils import ValueRef, OrderedSet
from caspian.curation.spark.spark_helpers import escape_sql_literal, sql_text_safe_fqn, sql_quote
from caspian.curation.spark.spark_sql_catalog import is_partitioned_table, get_table_partition_by_columns

_log = logging.getLogger(__name__)

_dbt_context_modules = _dbt_base.get_context_modules

STANDARD_END_TIME_DELTA = timedelta(milliseconds=1)


def _cspn_context_modules() -> Dict[str, Dict[str, Any]]:
    from caspian.dbt import dbt_extn
    return {"caspian": {"dbt_extn": dbt_extn}, **_dbt_context_modules()}

def apply_checkpoint_schema_override(checkpoint_schema: str) -> None:
    """
    Redirect all checkpoint reads/writes to a different schema.
    Intended for Databricks testing — call once at dbt model init time
    by passing a runtime var, e.g. --vars '{cspn_sys_db: caspian_ig_dev.jsum}'
    """
    if checkpoint_schema:
        checkpoints.Checkpoint.override_table_name(checkpoint_schema)
        _log.info(f"Checkpoint schema override applied: {checkpoint_schema}")

_dbt_base.get_context_modules = _cspn_context_modules


def read_config_meta(config: RuntimeConfigObject):
    _meta = config.model.config.extra.get('meta') or {}
    _model_meta = config.model.meta or {}

    return {**_meta, **_model_meta}


def generic_sql_exec(run_query: typing.Callable[[str], typing.Any]) -> GenericSQLExecWithTupleResults:
    def _exec_load_sql(sql: str) -> typing.List[typing.Tuple[typing.Any, ...]]:
        return [row.values() for row in run_query(sql)]

    return _exec_load_sql


def _fully_qualified_source_name(source) -> str:
    table_name = source.identifier if getattr(source, 'identifier', None) else source.table
    if source.database and source.schema:
        return f"{source.database}.{source.schema}.{table_name}"
    if source.schema:
        return f"{source.schema}.{table_name}"
    return str(source)


def _normalize_checkpoint_ds_name(raw_ds_name: str, source) -> str:
    ds_name = (raw_ds_name or '').strip()
    if not ds_name:
        return _fully_qualified_source_name(source)

    parts = [p for p in ds_name.split('.') if p]
    if len(parts) >= 3:
        return ds_name

    if len(parts) == 2 and source.database:
        return f"{source.database}.{parts[0]}.{parts[1]}"

    if len(parts) == 1 and source.database and source.schema:
        return f"{source.database}.{source.schema}.{parts[0]}"

    return ds_name


def load_standard_dataset_checkpoint(run_query: typing.Callable,
                                     config: RuntimeConfigObject,
                                     source) -> checkpoints.Checkpoint:
    meta = read_config_meta(config)
    app_name = meta.get('checkpoint_app_name') or config.model.package_name
    ds_name = _normalize_checkpoint_ds_name(meta.get('checkpoint_ds_name'), source)
    pipeline_name = meta.get('checkpoint_pipeline_name') or config.model.alias

    _log.info(f"Checkpoint key used app_name={app_name}, pipeline={pipeline_name}, ds={ds_name}")

    return checkpoints.read_checkpoint(generic_sql_exec(run_query),
                                       app_name=app_name,
                                       pipeline=pipeline_name,
                                       ds=ds_name)


def generate_sql_save_standard_dataset_checkpoint(checkpoint: checkpoints.Checkpoint) -> str:
    upsert_sql = ValueRef()

    def capture_sql(s: str):
        upsert_sql.value = s

    checkpoints.write_checkpoint(capture_sql, checkpoint)

    return upsert_sql.value


def generate_standard_source_table_load_filter_clause(run_query,
                                                      source: BaseRelation,
                                                      config: RuntimeConfigObject,
                                                      table_partition: str):
    meta = read_config_meta(config)
    checkpoint = load_standard_dataset_checkpoint(run_query, config, source)
    load_type, catchup_strategy = read_load_type_and_catch_up_strategy(meta)

    source_db = f"{source.database}.{source.schema}" if source.database else source.schema

    candidates = source_datasets.filter_partitions(source_db,
                                                   source.table,
                                                   checkpoint,
                                                   catchup_strategy,
                                                   generic_sql_exec(run_query),
                                                   table_partition
                                                   )

    return source_datasets.sql_filter_clause(candidates)


def commit_checkpoints(run_query, config: RuntimeConfigObject, run_id):
    sql_exec = generic_sql_exec(run_query)
    values = []
    for checkpoint, new_value in CheckpointMemoryStore.items():
        checkpoints.write_checkpoint(sql_exec, checkpoint, new_value)
        values.append(f"({escape_sql_literal(checkpoint.key)}, {escape_sql_literal(new_value)})")
    #miscutils.set_return_values(dict(miscutils.get_all_metrics()))
    if values:
        echo_sql = f"SELECT k,v FROM VALUES {','.join(values)} as T(k,v)"
    else:
        echo_sql = ""

    return echo_sql


def generate_dbt_surrogate_key(config: RuntimeConfigObject):
    meta = read_config_meta(config)
    surrogate_key_col_list = meta['surrogate_key_cols']

    return surrogate_key_col_list


def generate_audit_columns(config: RuntimeConfigObject, default_audit_col_list: list, run_id):
    meta = read_config_meta(config)
    if 'audit_column_list' in meta:
        audit_col_list = meta['audit_column_list']
    else:
        audit_col_list = default_audit_col_list
    audit_column_clause = source_datasets.get_audit_columns(audit_col_list, run_id)

    return audit_column_clause


def get_upsert_columns_dbt(dest_col_list):
    dest_columns_coalesce_list = []
    # dest_col_list.remove('`unique_col`')#
    for item in dest_col_list:
        dest_columns_coalesce_list.append(f""" coalesce(source_data.{sql_quote(item)},temp_tbl.{sql_quote(item)} )
         as {sql_quote(item)} """)
    # dest_columns_coalesce_list.append('source_data.`unique_col`')#
    dest_cols_csv = ','.join(dest_columns_coalesce_list)

    return dest_cols_csv


def generate_uuid() -> str:
    uuid_str = str(uuid.uuid4()).strip().replace('-', '_')

    return uuid_str


def generate_temp_tbl_sql_for_upsert(columns, target, source, unique_key, temp_db, temp_table):
    upsert_columns_coalesce_list = get_upsert_columns_dbt(columns)
    stmt = f""" create table { sql_text_safe_fqn (temp_db, temp_table) } as
TBLPROPERTIES (
    'delta.enableIcebergCompatV2' = 'true',
    'delta.universalFormat.enabledFormats' = 'iceberg'
)
with
temp_tbl as (select *
             from { target } ),
source_data as (select *
                from { source } ) select { upsert_columns_coalesce_list }
                                  from temp_tbl
                                  full outer join source_data on temp_tbl. { unique_key } = source_data.{ unique_key }
        """
    return stmt


def generate_trunc_sql(schema, table):
    stmt = f" truncate table {sql_text_safe_fqn(schema, table)} "

    return stmt


def generate_upsert_sql(run_query, schema, table, temp_db, temp_table, config: RuntimeConfigObject):
    part_col_clause = " "
    cluster_by_clause = " "
    meta = read_config_meta(config)
    if is_partitioned_table(schema, table, run_query):
        part_col_list = get_table_partition_by_columns(schema, table, run_query)
        if part_col_list is not None:
            part_cols = ','.join(part_col_list)
            part_col_clause = f" partition({part_cols}) "
        cluster_by_columns = meta.get("cluster_by", [])
        if cluster_by_columns:
            cluster_by_clause = " cluster by " + (", ".join([sql_quote(c) for c in cluster_by_columns]))
    stmt = f""" Insert overwrite table {sql_text_safe_fqn(schema, table)} {part_col_clause}
        Select * from {sql_text_safe_fqn(temp_db, temp_table)} {cluster_by_clause}"""

    return stmt


def get_formatted_query_with_table(col_list, table):
    final_col_list = []
    for item in col_list:
        final_col_list.append(f""" {table}.{sql_quote(item)}
         """)
    dest_cols_csv = ','.join(final_col_list)

    return dest_cols_csv


def generate_temp_tbl_sql_for_upsert_scd2(columns, target, audit_cols, source, unique_key, temp_db, temp_table,
                                          cycle_date, run_id):
    upsert_scd2_target_columns = columns
    audit_columns = audit_cols
    audit_column_clause = source_datasets.get_audit_columns(audit_columns, run_id)
    source_columns = list(OrderedSet(upsert_scd2_target_columns) - OrderedSet(audit_columns) - OrderedSet(
        ['eff_from', 'eff_to']))
    # We are creating a table to identify the unchanged, updated, expired and newly inserted records.
    stmt = f"""create table { sql_text_safe_fqn (temp_db, temp_table) }
TBLPROPERTIES (
    'delta.enableIcebergCompatV2' = 'true',
    'delta.universalFormat.enabledFormats' = 'iceberg'
)
as
with
source as (select  * from { source } ),
target as (select * from { target } ),
new_records as (select { get_formatted_query_with_table (source_columns, 'source') },
cast ('{cycle_date}' as timestamp) as eff_from, source.eff_to, { audit_column_clause } from source left join target on
source.{ unique_key } = target.{ unique_key } where target.{ unique_key } is null),
updated_records as
(select { get_formatted_query_with_table (source_columns, 'source') },
cast ('{cycle_date}' as timestamp) as eff_from, cast ('' as timestamp) as eff_to, target.SYS_CREATED,
target.SYS_CREATED_BY_NAME,
current_timestamp
() as SYS_UPDATED, source.SYS_UPDATED_BY_NAME,
target.cspn_id_key as tgt_sg_key from source inner join target on source.{ unique_key } = target.{ unique_key } where
source.cksum != target.cksum and target.eff_to is null),
modified_keys as
(select  tgt_sg_key from updated_records),
expired_records as
(select { get_formatted_query_with_table (source_columns, 'target') },
target.eff_from, cast ('{cycle_date}' as timestamp) as eff_to, target.SYS_CREATED, target.SYS_CREATED_BY_NAME,
current_timestamp() as SYS_UPDATED,
target.SYS_UPDATED_BY_NAME from target inner join modified_keys on target.cspn_id_key = modified_keys.tgt_sg_key where
target.eff_to is null),
unchanged_records as
(select   target.*
 from target
      left outer join
      modified_keys on target.cspn_id_key = modified_keys.tgt_sg_key
 where modified_keys.tgt_sg_key is null)
select { ',' . join (upsert_scd2_target_columns) } from updated_records union
select { ',' . join (upsert_scd2_target_columns) } from expired_records union
select { ',' . join (upsert_scd2_target_columns) } from unchanged_records union
select { ',' . join (upsert_scd2_target_columns) } from new_records
            """
    _log.debug(f"upsert query {stmt}")
    return stmt


def generate_scd2_merge_sql(columns, target, audit_cols, source, unique_key, app_cycle_date):
    upsert_scd2_target_columns = columns
    audit_columns = audit_cols
    source_columns = list(OrderedSet(upsert_scd2_target_columns) - OrderedSet(audit_columns) - OrderedSet(
        ['eff_from', 'eff_to']))

    # The first select  will either UPDATE the current data or INSERT the new data
    # The second insert will insert the updated data
    # -- Setting the mergeKey to NULL forces these rows to NOT MATCH and be INSERTed.
    # For more details, please refer
    # https://docs.databricks.com/_static/notebooks/merge-in-scd-type-2.html

    stmt = f""" Merge into {target} as target using
    ( Select source.{unique_key} as mergeKey, source.* from {source} as source
    union all
    Select NULL as merge_key, source.* from
    {source} source join {target} as target on source.{unique_key} = target.{unique_key}
    where source.cksum <> target.cksum and target.eff_to is null
    ) staged_data
    on target.{unique_key} = mergeKey
    WHEN MATCHED and target.cksum <> staged_data.cksum and target.eff_to is null THEN
    UPDATE SET eff_to = '{app_cycle_date}', SYS_UPDATED = current_timestamp()
    WHEN NOT MATCHED THEN
    INSERT({','.join(source_columns)}, eff_from,eff_to,{','.join(audit_columns)})
    VALUES( {get_formatted_query_with_table(source_columns, 'staged_data')},
    '{app_cycle_date}',cast('' as timestamp) ,
    {get_formatted_query_with_table(audit_cols, 'staged_data')} )  """
    _log.debug(f"scd2 merge query {stmt}")
    return stmt


def generate_match_merge_temp_tbl_query(columns, target, audit_cols, domain, source,
                                        unique_key, temp_db, temp_table, part_col='partitiondate'):
    upsert_scd2_target_columns = columns
    source_columns = list(OrderedSet(upsert_scd2_target_columns))
    _log.debug(f"match merge target column list {upsert_scd2_target_columns}")
    _log.debug(f"match merge source column list {source_columns}")
    _log.debug(f"get_formatted_query_with_table {get_formatted_query_with_table(source_columns, 'source')}")

    stmt = f""" with
    source as (select * from {source} ),
    target as (select t.* from {target} t inner join source on t.{part_col} = source.{part_col}),
    new_records as (select {get_formatted_query_with_table(source_columns, 'source')} from source left join target on
    source.{unique_key} = target.{unique_key} where target.{unique_key} is null),
    updated_records as
    (select {get_formatted_query_with_table(source_columns, 'source')},
    target.cspn_id_key as tgt_sg_key from source inner join target on source.{unique_key} = target.{unique_key} where
    source.cksum != target.cksum),
    modified_keys as
    (select tgt_sg_key from updated_records),
    unchanged_records as
    (select target.*
     from target
          left outer join
          modified_keys on target.cspn_id_key = modified_keys.tgt_sg_key
     where modified_keys.tgt_sg_key is null)
    insert overwrite table {sql_text_safe_fqn(temp_db, temp_table)}
    select {','.join(upsert_scd2_target_columns)} from updated_records union
    select {','.join(upsert_scd2_target_columns)} from unchanged_records union
    select {','.join(upsert_scd2_target_columns)} from new_records
    """
    _log.debug(f"match merge query {stmt}")
    return stmt


def generate_match_merge_temp_tbl_query_v2(columns, target, audit_cols, domain, source,
                                           unique_key, temp_db, temp_table, part_col='partitiondate'):
    upsert_scd2_target_columns = columns
    source_columns = list(OrderedSet(upsert_scd2_target_columns))
    _log.debug(f"match merge target column list {upsert_scd2_target_columns}")
    _log.debug(f"match merge source column list {source_columns}")
    _log.debug(f"get_formatted_query_with_table {get_formatted_query_with_table(source_columns, 'source')}")

    stmt = f""" with
    source as (select * from {source} ),
    target as (select t.* from {target} t inner join source on t.{part_col} = source.{part_col}),
    new_records as (select {get_formatted_query_with_table(source_columns, 'source')} from source left join target on
    source.{unique_key} = target.{unique_key} where target.{unique_key} is null),
    updated_records as
    (select {get_formatted_query_with_table(source_columns, 'source')},
    target.dlrowuid as tgt_sg_key from source inner join target on source.{unique_key} = target.{unique_key} where
    source.dlchecksumvalue != target.dlchecksumvalue),
    modified_keys as
    (select tgt_sg_key from updated_records),
    unchanged_records as
    (select target.*
     from target
          left outer join
          modified_keys on target.dlrowuid = modified_keys.tgt_sg_key
     where modified_keys.tgt_sg_key is null)
    insert overwrite table {sql_text_safe_fqn(temp_db, temp_table)}
    select {','.join(upsert_scd2_target_columns)} from updated_records union
    select {','.join(upsert_scd2_target_columns)} from unchanged_records union
    select {','.join(upsert_scd2_target_columns)} from new_records
    """
    _log.debug(f"match merge query {stmt}")
    return stmt


def generate_match_merge_reference_temp_tbl_query(columns, target, audit_cols, domain, source, unique_key, temp_db,
                                                  temp_table, app_cycle_date, part_col='partitiondate'):
    upsert_scd2_target_columns = columns
    source_columns = list(OrderedSet(upsert_scd2_target_columns))
    _log.debug(f"match merge target column list {upsert_scd2_target_columns}")
    _log.debug(f"match merge source column list {source_columns}")
    _log.debug(f"get_formatted_query_with_table {get_formatted_query_with_table(source_columns, 'source')}")
    upsert_scd2_target_columns.remove(part_col)
    stmt = f""" with
    src as (select * from {source}),
    tgt as (select * from {target}),
    new_plus_updated_records as (select {get_formatted_query_with_table(source_columns, 'src')} from src),
    unchanged_records as (select t1.* from tgt t1 left join src t2
    on t1.{unique_key} = t2.{unique_key}
    where t2.{unique_key} is null)
    insert overwrite table {sql_text_safe_fqn(temp_db, temp_table)}
    select {','.join(upsert_scd2_target_columns)}, partitiondate from new_plus_updated_records union
    select {','.join(upsert_scd2_target_columns)}, cast('{app_cycle_date}' as date) as partitiondate from
    unchanged_records
    """
    _log.debug(f"match merge reference query {stmt}")
    return stmt


def generate_match_merge_alt_v2_temp_tbl_query(columns, target, audit_cols, domain, source, unique_key, temp_db,
                                               temp_table, action_code_col=None, part_col='partitiondate'):
    upsert_scd2_target_columns = columns
    source_columns = list(OrderedSet(upsert_scd2_target_columns))
    _log.debug(f"match merge target column list {upsert_scd2_target_columns}")
    _log.debug(f"match merge source column list {source_columns}")
    _log.debug(f"get_formatted_query_with_table {get_formatted_query_with_table(source_columns, 'source')}")
    _log.info(f"action code col value is {action_code_col}")

    if action_code_col:
        insert_overwrite_statement = f"""
        insert overwrite table {sql_text_safe_fqn(temp_db, temp_table)}
        select * from (select {','.join(upsert_scd2_target_columns)} from new_plus_updated_records
        union
        select {','.join(upsert_scd2_target_columns)} from unchanged_records)
        where {action_code_col} IS NULL or {action_code_col} <> 'D'
        """
    else:
        insert_overwrite_statement = f"""
        insert overwrite table {sql_text_safe_fqn(temp_db, temp_table)}
        select {','.join(upsert_scd2_target_columns)} from new_plus_updated_records union
        select {','.join(upsert_scd2_target_columns)} from unchanged_records
        """

    stmt = f""" with
    src as (select * from {source}),
    dist_part_dates as (select distinct {part_col} from {source}),
    tgt as (select t1.* from {target} t1 inner join dist_part_dates t2 on t1.{part_col} = t2.{part_col}),
    new_plus_updated_records as (select {get_formatted_query_with_table(source_columns, 'src')} from src),
    unchanged_records as (select t3.* from tgt t3 left join src t4
    on t3.{part_col} = t4.{part_col} and t3.{unique_key} = t4.{unique_key}
    where t4.{unique_key} is null)
    {insert_overwrite_statement}
    """
    _log.debug(f"match merge alt v2 query {stmt}")
    return stmt


def cspn_generate_delete_merge_temp_tbl_query(target, source, unique_key):
    stmt = f""" Merge into {target} as target using (select distinct {unique_key} from {source}) as source
        on target.{unique_key} = source.{unique_key}
        WHEN MATCHED THEN DELETE
        """
    _log.debug(f"delete merge query {stmt}")
    return stmt


def add_caspian_utils_macros_path_variable():
    def _find_caspian_utils():
        import caspian.dbt as _dbt
        return Path(_dbt.__file__).parent / "caspian_utils"

    def customize_project_raw_dict(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            raw_project_dict = kwargs['project_dict']

            macros_paths: typing.List = raw_project_dict.get("macro-paths")
            cspn_utils = _find_caspian_utils()

            for i, p in enumerate(macros_paths):
                p = p.format(CASPIAN_UTILS=str(cspn_utils))
                if Path(p).resolve() == cspn_utils:
                    macros_paths[i] = p
                    break

            return fn(*args, **kwargs)

        return wrapper

    import dbt
    dbt.config.project.PartialProject.from_dicts = customize_project_raw_dict(
        dbt.config.project.PartialProject.from_dicts)


def monkey_patch_dbt():
    add_caspian_utils_macros_path_variable()


def delete_app_cycle_data(run_query, table, app_cycle_date):
    query = f""" delete from {table} where as_of_date = '{app_cycle_date}' """
    return query


def is_skip_metrics(config: RuntimeConfigObject):
    meta = read_config_meta(config)
    return miscutils.to_bool(meta.get("skip_metrics", "False"))


""" Adding this method to support xcom_pull.When no value is pushed to xcom
(for special cases like foundation and consumption in same DAG)"""


def cspn_add_default_metric(temporary_db):
    miscutils.add_metric("platform", "caspian")
    fields = dict(miscutils.get_all_metrics())
    miscutils.set_return_values(fields)
    stmt = f"USE {temporary_db}"
    return stmt


def generate_bitemporal_merge_sql(
    columns, target, audit_cols, source, unique_key, app_cycle_prior_day, app_cycle_date, curr_timestamp,
    action_code_col=None, bitemporal_col_version='v1'
):
    dl_system_end_timestamp_for_expired = curr_timestamp - STANDARD_END_TIME_DELTA

    upsert_scd2_target_columns = columns
    audit_columns = audit_cols

    bitemporal_column_map, dl_checksum_column = get_bitemporal_column_names(bitemporal_col_version)

    dl_current_indicator_column = bitemporal_column_map.get('dl_current_indicator_col')
    dl_business_start_column = bitemporal_column_map.get('dl_business_start_col')
    dl_business_end_column = bitemporal_column_map.get('dl_business_end_col')
    dl_system_start_column = bitemporal_column_map.get('dl_system_start_col')
    dl_system_end_column = bitemporal_column_map.get('dl_system_end_col')

    source_columns = list(OrderedSet(upsert_scd2_target_columns) - OrderedSet(audit_columns) - OrderedSet(
        list(bitemporal_column_map.values())))

    action_code_stmt = ""
    if action_code_col:
        action_code_stmt = f"""
            AND ({action_code_col} IS NULL OR {action_code_col} <> 'D')
        """
    stmt = f"""
    MERGE INTO {target} AS target USING(
      WITH
        reactivate_recs AS  (
           SELECT DISTINCT {unique_key} FROM {target} target WHERE target.{dl_current_indicator_column} = 'N'
           EXCEPT
           SELECT DISTINCT {unique_key} FROM {target} target WHERE target.{dl_current_indicator_column} = 'Y'
        ),
        source_ingested AS (
          SELECT
            source.*,
            target.{unique_key} AS target_unique_key,
            target.{dl_checksum_column} AS target_dl_checksum_value,
            target.{dl_current_indicator_column} AS target_dl_current_indicator
          FROM {source} source LEFT JOIN {target} target
          ON (source.{unique_key} = target.{unique_key} AND target.{dl_current_indicator_column} = 'Y'
          )
        )
       SELECT
        NULL AS mergeKey,
        CASE WHEN target_unique_key is NULL THEN
         CASE WHEN reactivate_recs.{unique_key} IS NULL THEN 'new'
         ELSE 'reactivate' END
        ELSE 'update' END AS record_type,
        source_ingested.*
      FROM source_ingested LEFT OUTER JOIN reactivate_recs
      ON source_ingested.{unique_key} = reactivate_recs.{unique_key}
      WHERE source_ingested.{dl_checksum_column} <> coalesce(source_ingested.target_dl_checksum_value, 'NA')
      {action_code_stmt}
      UNION ALL
      SELECT
        source_ingested.{unique_key} AS mergeKey,
        'update' AS record_type,
        source_ingested.*
      FROM source_ingested
      WHERE source_ingested.{dl_checksum_column} <> coalesce(source_ingested.target_dl_checksum_value, 'NA')
      AND target_unique_key is NOT NULL AND target_dl_current_indicator = 'Y'
    ) staged_data
    ON target.{unique_key} = mergeKey AND target.{dl_current_indicator_column} = 'Y'
    WHEN MATCHED THEN
      UPDATE SET
        {dl_business_end_column} = cast('{app_cycle_prior_day}' AS date),
        {dl_system_end_column} = cast('{dl_system_end_timestamp_for_expired}' as timestamp),
        {dl_current_indicator_column} = CASE
            WHEN target.dl_business_start_date > cast('{app_cycle_prior_day}' AS date)
            THEN 'I'
            ELSE 'N'
          END
    WHEN NOT MATCHED THEN
      INSERT(
        {','.join(source_columns)}{','.join(audit_columns)},{dl_current_indicator_column}, {dl_business_start_column},
        {dl_business_end_column}, {dl_system_start_column}, {dl_system_end_column}
      )
      VALUES (
        {get_formatted_query_with_table(source_columns, 'staged_data')}
        {get_formatted_query_with_table(audit_cols, 'staged_data')}, 'Y',
        (CASE
          WHEN staged_data.record_type = 'new' THEN to_date('1900-01-01', 'yyyy-MM-dd')
          WHEN staged_data.record_type = 'reactivate' THEN to_date('{app_cycle_date}', 'yyyy-MM-dd')
          WHEN staged_data.record_type = 'update' THEN to_date('{app_cycle_date}', 'yyyy-MM-dd')
          ELSE to_date('1900-01-01', 'yyyy-MM-dd') END
        ),
        to_date('9999-12-31', 'yyyy-MM-dd'),
        cast('{curr_timestamp}' as timestamp),
        cast('9999-12-31'||' 23:59:59' as timestamp)
      )
    """
    _log.debug(f" scd2 merge query {stmt}")
    return stmt


def generate_bitemporal_merge_using_source_date_sql(
    columns, target, audit_cols, source, unique_key, curr_timestamp, action_code_col=None, start_date_col=None,
    end_date_col=None, bitemporal_col_version='v1'
):
    dl_system_end_timestamp_for_expired = curr_timestamp - STANDARD_END_TIME_DELTA

    upsert_scd2_target_columns = columns
    audit_columns = audit_cols

    bitemporal_column_map, dl_checksum_column = get_bitemporal_column_names(bitemporal_col_version)

    dl_current_indicator_column = bitemporal_column_map.get('dl_current_indicator_col')
    dl_business_start_column = bitemporal_column_map.get('dl_business_start_col')
    dl_business_end_column = bitemporal_column_map.get('dl_business_end_col')
    dl_system_start_column = bitemporal_column_map.get('dl_system_start_col')
    dl_system_end_column = bitemporal_column_map.get('dl_system_end_col')

    source_columns = list(OrderedSet(upsert_scd2_target_columns) - OrderedSet(audit_columns) - OrderedSet(
        list(bitemporal_column_map.values())))

    action_code_stmt = ""
    if action_code_col:
        action_code_stmt = f"""
            AND ({action_code_col} IS NULL OR {action_code_col} <> 'D')
        """
    if end_date_col:
        end_date_stmt = f"""source.{end_date_col}"""
        business_end_date_stmt = f""" date_sub(CAST(target_{dl_business_start_column} as DATE), 1)"""
    else:
        end_date_stmt = "to_date('9999-12-31', 'yyyy-MM-dd')"
        business_end_date_stmt = f"""date_sub(CAST(source.{dl_business_start_column} as DATE), 1)"""
    stmt = f"""
    MERGE INTO {target} AS target USING(
      WITH
        source_ingested AS (
          SELECT
            source.*,
            target.{unique_key} AS target_unique_key,
            target.{dl_checksum_column} AS target_dl_checksum_value,
            target.{dl_current_indicator_column} AS target_dl_current_indicator,
            target.{dl_business_start_column} AS target_dl_business_start_date,
            {end_date_stmt} AS default_end_date
          FROM {source} source LEFT JOIN {target} target
          ON (source.{unique_key} = target.{unique_key} AND target.{dl_current_indicator_column} = 'Y'
        )
      )
      SELECT
        NULL AS mergeKey,
        CASE WHEN target_unique_key is NULL THEN 'new' ELSE 'update' END AS record_type,
        source_ingested.*
      FROM source_ingested
      WHERE source_ingested.{dl_checksum_column} <> coalesce(source_ingested.target_dl_checksum_value, 'NA')
      {action_code_stmt}
      UNION ALL
      SELECT
        source_ingested.{unique_key} AS mergeKey,
        'update' AS record_type,
        source_ingested.*
      FROM source_ingested
      WHERE source_ingested.{dl_checksum_column} <> coalesce(source_ingested.target_dl_checksum_value, 'NA')
      AND target_unique_key is NOT NULL AND target_dl_current_indicator = 'Y'
    ) staged_data
    ON target.{unique_key} = mergeKey AND target.{dl_current_indicator_column} = 'Y'
    WHEN MATCHED THEN
      UPDATE SET
        {dl_business_end_column} = {business_end_date_stmt},
        {dl_system_end_column} = cast('{dl_system_end_timestamp_for_expired}' as timestamp),
        {dl_current_indicator_column} = CASE
              WHEN target.dl_business_start_date > {business_end_date_stmt}
              THEN 'I'
              ELSE 'N'
            END
    WHEN NOT MATCHED THEN
      INSERT(
        {','.join(source_columns)}{','.join(audit_columns)},{dl_current_indicator_column}, {dl_business_start_column},
        {dl_business_end_column}, {dl_system_start_column}, {dl_system_end_column}
      )
      VALUES (
        {get_formatted_query_with_table(source_columns, 'staged_data')}
        {get_formatted_query_with_table(audit_cols, 'staged_data')},
        CASE WHEN default_end_date < current_date() THEN 'N' ELSE 'Y' END,
        staged_data.{start_date_col},
        default_end_date,
        cast('{curr_timestamp}' as timestamp),
        CASE WHEN default_end_date < current_date()
        THEN cast('{curr_timestamp}' as timestamp) ELSE cast('9999-12-31'||' 23:59:59' as timestamp) END
      )
    """
    _log.debug(f" scd2 merge query {stmt}")
    return stmt


def generate_bitemporal_update_expire_rows(target, source_tmp, unique_key, app_cycle_prior_day, app_cycle_date,
                                           curr_timestamp, bitemporal_col_version='v1'):

    dl_system_end_timestamp_for_expired = curr_timestamp - STANDARD_END_TIME_DELTA

    if bitemporal_col_version == 'v2':
        dl_system_end_col = 'dl_system_end_timestamp'
    else:
        dl_system_end_col = 'dl_system_end_date'

    stmt = f"""
    MERGE INTO {target} AS target USING(
    SELECT source.{unique_key} AS mergeKey
    FROM {source_tmp} AS source
    INNER JOIN {target} AS target_cur
        ON source.{unique_key} = target_cur.{unique_key}
    AND target_cur.dl_current_indicator = 'Y'
    WHERE source.dl_checksum_value <> coalesce(target_cur.dl_checksum_value, 'NA')
    ) AS stage_data
    ON target.{unique_key} = stage_data.mergeKey AND target.dl_current_indicator = 'Y'
    WHEN MATCHED THEN
      UPDATE SET
      dl_business_end_date = cast('{app_cycle_prior_day}' as date),
      {dl_system_end_col} = cast('{dl_system_end_timestamp_for_expired}' as timestamp),
      dl_current_indicator = CASE
         WHEN target.dl_business_start_date > cast('{app_cycle_prior_day}' AS date)
          THEN  'I'
          ELSE 'N'
        END
        ;
    """
    _log.debug(f"scd2 update sql to expire previously active records : {stmt}")
    return stmt


def generate_balance_bitemporal_update_expire_rows(target, source, unique_key, app_cycle_prior_day, app_cycle_date,
                                           curr_timestamp, bitemporal_col_version='v1'):

    dl_system_end_timestamp_for_expired = curr_timestamp - STANDARD_END_TIME_DELTA

    if bitemporal_col_version == 'v2':
        dl_system_end_col = 'dl_system_end_timestamp'
    else:
        dl_system_end_col = 'dl_system_end_date'

    stmt = f"""
    MERGE INTO {target} AS target USING(
    WITH
      source AS (SELECT * FROM {source}),
      target AS (SELECT * FROM {target} WHERE dl_current_indicator = 'Y')
      SELECT target.{unique_key} AS mergeKey
      FROM target LEFT JOIN source
      ON target.{unique_key} = source.{unique_key}
      WHERE source.{unique_key} is NULL
    ) stage_data
    ON target.{unique_key} = mergeKey AND target.dl_current_indicator = 'Y'
    WHEN MATCHED THEN
      UPDATE SET
      {dl_system_end_col} = cast('{dl_system_end_timestamp_for_expired}' as timestamp),
      dl_current_indicator = 'I'
    """
    _log.debug(f"scd2 update sql to expire previously active records : {stmt}")
    return stmt


def generate_balance_bitemporal_merge_sql(
        columns, target, audit_cols, source, unique_key, curr_timestamp, as_of_col, detect_change_flag=None,
        action_code_col=None, bitemporal_col_version='v1', capture_last_update_flag=None,
        transaction_cancel_flag=False):

    dl_system_end_timestamp_for_expired = curr_timestamp - STANDARD_END_TIME_DELTA

    upsert_scd2_target_columns = columns
    audit_columns = audit_cols

    bitemporal_column_map, dl_checksum_column = get_bitemporal_column_names(bitemporal_col_version)

    dl_current_indicator_column = bitemporal_column_map.get('dl_current_indicator_col')
    dl_system_start_column = bitemporal_column_map.get('dl_system_start_col')
    dl_system_end_column = bitemporal_column_map.get('dl_system_end_col')
    dl_last_update_column = "dl_last_update_timestamp"

    source_columns = list(OrderedSet(upsert_scd2_target_columns) - OrderedSet(audit_columns) - OrderedSet(
        [dl_current_indicator_column, dl_system_start_column, dl_system_end_column, dl_last_update_column]))

    action_code_stmnt = ""
    detect_change_stmnt = ""

    if action_code_col:
        if not transaction_cancel_flag:
            action_code_stmnt = f""" and ({action_code_col} IS NULL OR {action_code_col} <> 'D') """
            dl_current_indicator_stmnt = f""" CASE WHEN staged_data.{action_code_col} = 'D' THEN 'D' ELSE 'I' END """
        else:
            dl_current_indicator_stmnt = "'D'"
    else:
        dl_current_indicator_stmnt = "'I'"

    if detect_change_flag:
        detect_change_stmnt = f""" and source_ingested.{dl_checksum_column} <>
                               coalesce(source_ingested.target_dlchecksumvalue, 'NA') """

    insert_col_list = f"""
        {','.join(source_columns)}{','.join(audit_columns)},{dl_current_indicator_column},{dl_system_start_column},
        {dl_system_end_column}
    """
    if transaction_cancel_flag:
        insert_col_values = f"""
            {get_formatted_query_with_table(source_columns, 'staged_data')}
            {get_formatted_query_with_table(audit_cols, 'staged_data')},
            CASE WHEN (staged_data.{action_code_col} IS NULL OR staged_data.{action_code_col} <> 'D') THEN 'Y'
            ELSE 'D' END,
            cast('{curr_timestamp}' as timestamp),
            cast('9999-12-31'||' 23:59:59' as timestamp)
        """
    else:
        insert_col_values = f"""
            {get_formatted_query_with_table(source_columns, 'staged_data')}
            {get_formatted_query_with_table(audit_cols, 'staged_data')}, 'Y',
            cast('{curr_timestamp}' as timestamp),
            cast('9999-12-31'||' 23:59:59' as timestamp)
        """
    dl_last_update_timestamp_stmt = ""

    if capture_last_update_flag:
        dl_last_update_timestamp_stmt = f", dl_last_update_timestamp = cast('{curr_timestamp}' as timestamp)"
        insert_col_list = f"{insert_col_list}, {dl_last_update_column}"
        insert_col_values = f"{insert_col_values}, cast('{curr_timestamp}' as timestamp)"

    stmt = f"""
        MERGE INTO {target} AS target USING(
        WITH
        source_dates as (select distinct {as_of_col} as asof_col from {source}),
        target_filtered as (select * from {target}
        where {as_of_col} in (select asof_col from source_dates) and {dl_current_indicator_column} = 'Y'),
        source_ingested as (
        select source.*, target_inner.{unique_key} as target_unique_key,
        target_inner.{dl_checksum_column} as target_dlchecksumvalue,
        target_inner.{dl_current_indicator_column} as target_dl_current_indicator
        from {source} source left join  target_filtered target_inner
        ON
        (source.{unique_key} = target_inner.{unique_key}
        and source.{as_of_col} = target_inner.{as_of_col} )
        )
        SELECT
        NULL as mergeKey,
        CASE WHEN target_unique_key is NULL THEN 'new' ELSE 'update' END as record_type,
        source_ingested.*
        FROM source_ingested where 1=1 {detect_change_stmnt} {action_code_stmnt}
        UNION ALL
        SELECT
        source_ingested.{unique_key} as mergeKey, 'update' as record_type, source_ingested.*
        FROM source_ingested where 1=1
        {detect_change_stmnt}
        AND target_unique_key is NOT NULL AND target_dl_current_indicator = 'Y') staged_data
        ON target.{unique_key} = mergeKey
        and target.{as_of_col} = staged_data.{as_of_col}
        and target.{dl_current_indicator_column} = 'Y'
        WHEN MATCHED THEN
        UPDATE SET
        {dl_system_end_column} = cast('{dl_system_end_timestamp_for_expired}' as timestamp),
        {dl_current_indicator_column} = {dl_current_indicator_stmnt}
        {dl_last_update_timestamp_stmt}
        WHEN NOT MATCHED THEN
        INSERT({insert_col_list})
        VALUES ({insert_col_values}) """
    _log.debug(f" Balance_Bitemporal merge query {stmt}")
    return stmt


def generate_expire_merge_master_bitemporal_expire_sql(
        target, source, unique_key, app_cycle_prior_day, app_cycle_date, curr_timestamp):
    dl_system_end_timestamp_for_expired = curr_timestamp - STANDARD_END_TIME_DELTA
    stmt = f""" Merge into {target} as target
                using (select distinct {unique_key} from {source}) as source
                on target.{unique_key} = source.{unique_key} and target.dl_current_indicator = 'Y'
                WHEN MATCHED THEN
                  UPDATE SET
                  dl_business_end_date = cast('{app_cycle_prior_day}' as date),
                  dl_system_end_timestamp  = cast('{dl_system_end_timestamp_for_expired}' as timestamp),
                  dl_current_indicator = CASE
                     WHEN target.dl_business_start_date > cast('{app_cycle_prior_day}' AS date)
                     THEN  'I'
                     ELSE 'N'
                  END
                """
    _log.debug(f"scd2 update sql to expire previously active records : {stmt}")
    return stmt


def generate_expire_merge_master_bitemporal_merge_sql(
    columns, target, audit_cols, source, unique_key, app_cycle_prior_day, app_cycle_date, curr_timestamp,
    action_code_col=None
):
    dl_system_end_timestamp_for_expired = curr_timestamp - STANDARD_END_TIME_DELTA
    upsert_scd2_target_columns = columns
    audit_columns = audit_cols
    source_columns = list(OrderedSet(upsert_scd2_target_columns) - OrderedSet(audit_columns) - OrderedSet(
        ['dl_current_indicator', 'dl_business_start_date', 'dl_business_end_date', 'dl_system_start_timestamp',
         'dl_system_end_timestamp']))
    action_code_stmt = "1=1"
    if action_code_col:
        action_code_stmt = f"""
            ({action_code_col} IS NULL OR {action_code_col} <> 'D')
        """
    stmt = f"""
    MERGE INTO {target} AS target USING(
      WITH
        source_ingested AS (
          SELECT
            source.*,
            target.{unique_key} AS target_unique_key,
            expired_rec.{unique_key} AS expired_unique_key,
            target.dl_current_indicator AS target_dl_current_indicator
          FROM {source} source LEFT JOIN {target} target
          ON (source.{unique_key} = target.{unique_key} AND target.dl_current_indicator = 'Y')
          LEFT JOIN ( SELECT distinct {unique_key} FROM {target} where dl_current_indicator = 'N') expired_rec
          ON source.{unique_key} = expired_rec.{unique_key}
      )
      SELECT
        NULL AS mergeKey,
        CASE WHEN target_unique_key is NULL AND expired_unique_key is NULL THEN 'new' ELSE 'update' END AS record_type,
        source_ingested.*
      FROM source_ingested
      WHERE {action_code_stmt}
      UNION ALL
      SELECT
        source_ingested.{unique_key} AS mergeKey,
        'update' AS record_type,
        source_ingested.*
      FROM source_ingested
      WHERE target_unique_key is NOT NULL AND target_dl_current_indicator = 'Y'
    ) staged_data
    ON target.{unique_key} = mergeKey AND target.dl_current_indicator = 'Y'
    WHEN MATCHED THEN
      UPDATE SET
        dl_business_end_date = cast('{app_cycle_prior_day}' AS date),
        dl_system_end_timestamp = cast('{dl_system_end_timestamp_for_expired}' as timestamp),
        dl_current_indicator = CASE
         WHEN target.dl_business_start_date >  cast('{app_cycle_prior_day}' AS date)
          THEN  'I'
          ELSE 'N'
          END
    WHEN NOT MATCHED THEN
      INSERT(
        {','.join(source_columns)}{','.join(audit_columns)},dl_current_indicator, dl_business_start_date,
        dl_business_end_date, dl_system_start_timestamp, dl_system_end_timestamp
      )
      VALUES (
        {get_formatted_query_with_table(source_columns, 'staged_data')}
        {get_formatted_query_with_table(audit_cols, 'staged_data')}, 'Y',
        (CASE
          WHEN staged_data.record_type = 'new' THEN to_date('1900-01-01', 'yyyy-MM-dd')
          WHEN staged_data.record_type = 'update' THEN to_date('{app_cycle_date}', 'yyyy-MM-dd')
          ELSE to_date('1900-01-01', 'yyyy-MM-dd') END
        ),
        to_date('9999-12-31', 'yyyy-MM-dd'),
        cast('{curr_timestamp}' as timestamp),
        cast('9999-12-31'||' 23:59:59' as timestamp)
      )
    """
    _log.debug(f" scd2 merge query {stmt}")
    return stmt


def get_bitemporal_column_names(version):

    bitemporal_column_map = {
        'v1': {
            'dl_current_indicator_col': 'dl_current_indicator',
            'dl_business_start_col': 'dl_business_start_date',
            'dl_business_end_col': 'dl_business_end_date',
            'dl_system_start_col': 'dl_system_start_date',
            'dl_system_end_col': 'dl_system_end_date'
        },
        'v2': {
            'dl_current_indicator_col': 'dl_current_indicator',
            'dl_business_start_col': 'dl_business_start_date',
            'dl_business_end_col': 'dl_business_end_date',
            'dl_system_start_col': 'dl_system_start_timestamp',
            'dl_system_end_col': 'dl_system_end_timestamp'
        }
    }

    bitemporal_checksum_column_map = {'v1': 'dlchecksumvalue', 'v2': 'dl_checksum_value'}

    return bitemporal_column_map[version], bitemporal_checksum_column_map[version]
