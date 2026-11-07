import logging

from caspian.dbt import dbt_modules

_log = logging.getLogger(__name__)


def cspn_hello(run_query) -> str:
    """
    This function is python implementation of a sanity test macro. It is meant to be used
    by a test/check process which validate the deployment.
    :return:
    """
    exec_sql = dbt_modules.generic_sql_exec(run_query)
    return exec_sql("SELECT 'Hello from Caspian Dbt Extension' as Msg")[0][0]


def cspn_standard_source_table_load_filter(run_query, config, source, table_partition) -> str:
    return dbt_modules.generate_standard_source_table_load_filter_clause(run_query, source, config, table_partition)


def cspn_commit_checkpoints(run_query, config, run_id) -> str:
    return dbt_modules.commit_checkpoints(run_query, config, run_id)


def cspn_audit_columns(config, default_audit_col_list, run_id) -> str:
    return dbt_modules.generate_audit_columns(config, default_audit_col_list, run_id)


def cspn_surrogate_key(config) -> str:
    return dbt_modules.generate_dbt_surrogate_key(config)


def cspn_get_upsert_columns_dbt(dest_col_list) -> str:
    return dbt_modules.get_upsert_columns_dbt(dest_col_list)


def cspn_get_uuid() -> str:
    return dbt_modules.generate_uuid()


def cspn_generate_temp_tbl_query(columns, target, source, unique_key, temp_db, temp_table):
    return dbt_modules.generate_temp_tbl_sql_for_upsert(columns, target, source, unique_key, temp_db, temp_table)


def cspn_generate_trunc_query(schema, table):
    return dbt_modules.generate_trunc_sql(schema, table)


def cspn_generate_upsert_query(run_query, schema, table, temp_db, temp_table, config):
    return dbt_modules.generate_upsert_sql(run_query, schema, table, temp_db, temp_table, config)


def cspn_delete_app_cycle_data(run_query, table, app_cycle_date):
    return dbt_modules.delete_app_cycle_data(run_query, table, app_cycle_date)


def cspn_generate_scd2_temp_tbl_query(columns, target, audit_cols, source, unique_key, temp_db, temp_table, cycle_date,
                                      run_id):
    return dbt_modules.generate_temp_tbl_sql_for_upsert_scd2(columns, target, audit_cols, source,
                                                             unique_key, temp_db, temp_table, cycle_date, run_id)


def cspn_generate_scd2_merge_query(columns, target, audit_cols, source, unique_key, app_cycle_date):
    return dbt_modules.generate_scd2_merge_sql(columns, target, audit_cols, source, unique_key, app_cycle_date)


def cspn_generate_bitemporal_merge_query(columns, target, audit_cols, source, unique_key, app_cycle_prior_day,
                                         app_cycle_date, curr_timestamp, action_code_col,
                                         bitemporal_col_version='v1'):
    return dbt_modules.generate_bitemporal_merge_sql(columns, target, audit_cols, source, unique_key,
                                                     app_cycle_prior_day, app_cycle_date,
                                                     curr_timestamp, action_code_col, bitemporal_col_version)


def cspn_generate_balance_bitemporal_merge_query(columns, target, audit_cols, source, unique_key,
                                                 curr_timestamp, as_of_col, detect_change_flag, action_code_col,
                                                 bitemporal_col_version='v1'):
    return dbt_modules.generate_balance_bitemporal_merge_sql(columns, target, audit_cols, source, unique_key,
                                                             curr_timestamp, as_of_col, detect_change_flag,
                                                             action_code_col, bitemporal_col_version)


def cspn_generate_bitemporal_merge_using_source_date_sql(columns, target, audit_cols, source, unique_key,
                                                         curr_timestamp, action_code_col=None, start_date_col=None,
                                                         end_date_col=None, bitemporal_col_version='v1'):
    return dbt_modules.generate_bitemporal_merge_using_source_date_sql(columns, target, audit_cols, source,
                                                                       unique_key, curr_timestamp, action_code_col,
                                                                       start_date_col, end_date_col,
                                                                       bitemporal_col_version)


def cspn_generate_bitemporal_update_expire_rows(
    target, source, unique_key, app_cycle_prior_day, app_cycle_date, curr_timestamp, bitemporal_col_version='v1'
):
    return dbt_modules.generate_bitemporal_update_expire_rows(
        target, source, unique_key, app_cycle_prior_day, app_cycle_date, curr_timestamp, bitemporal_col_version
    )


def cspn_generate_balance_bitemporal_update_expire_rows(
    target, source, unique_key, app_cycle_prior_day, app_cycle_date, curr_timestamp, bitemporal_col_version='v1'
):
    return dbt_modules.generate_balance_bitemporal_update_expire_rows(
        target, source, unique_key, app_cycle_prior_day, app_cycle_date, curr_timestamp, bitemporal_col_version
    )


def cspn_generate_match_merge_temp_tbl_query(columns, target, audit_cols, domain, source, unique_key, temp_db,
                                             temp_table):
    return dbt_modules.generate_match_merge_temp_tbl_query(columns, target, audit_cols, domain, source,
                                                           unique_key, temp_db, temp_table)


def cspn_generate_match_merge_reference_temp_tbl_query(columns, target, audit_cols, domain, source, unique_key,
                                                       temp_db, temp_table, app_cycle_date):
    return dbt_modules.generate_match_merge_reference_temp_tbl_query(columns, target, audit_cols, domain, source,
                                                                     unique_key, temp_db, temp_table, app_cycle_date)


def cspn_generate_match_merge_alt_v2_temp_tbl_query(columns, target, audit_cols, domain, source, unique_key, temp_db,
                                                    temp_table, action_code_col):
    return dbt_modules.generate_match_merge_alt_v2_temp_tbl_query(columns, target, audit_cols, domain, source,
                                                                  unique_key, temp_db, temp_table, action_code_col)


def cspn_generate_match_merge_temp_tbl_query_v2(columns, target, audit_cols, domain, source, unique_key, temp_db,
                                                temp_table):
    return dbt_modules.generate_match_merge_temp_tbl_query_v2(columns, target, audit_cols, domain, source,
                                                              unique_key, temp_db, temp_table)


def cspn_generate_delete_merge_temp_tbl_query(target, source, unique_key):
    return dbt_modules.cspn_generate_delete_merge_temp_tbl_query(target, source, unique_key,)

def add_default_metric(temporary_db):
    return dbt_modules.cspn_add_default_metric(temporary_db)


def cspn_generate_expire_merge_master_bitemporal_expire_query(
        target, source, unique_key, app_cycle_prior_day, app_cycle_date, curr_timestamp):
    return dbt_modules.generate_expire_merge_master_bitemporal_expire_sql(
        target, source, unique_key, app_cycle_prior_day, app_cycle_date, curr_timestamp)


def cspn_generate_expire_merge_master_bitemporal_merge_query(
        columns, target, audit_cols, source, unique_key, app_cycle_prior_day, app_cycle_date, curr_timestamp,
        action_code_col):
    return dbt_modules.generate_expire_merge_master_bitemporal_merge_sql(
        columns, target, audit_cols, source, unique_key, app_cycle_prior_day, app_cycle_date, curr_timestamp,
        action_code_col)

def cspn_apply_checkpoint_schema_override(checkpoint_schema: str) -> str:
    """
    Call from a dbt model or macro to redirect checkpoint table to a test schema.
    Usage in dbt Jinja:
        {{ modules.caspian.dbt_extn.cspn_apply_checkpoint_schema_override(var('cspn_sys_db', '')) }}
    """
    dbt_modules.apply_checkpoint_schema_override(checkpoint_schema)
    return f"-- checkpoint schema set to: {checkpoint_schema}"