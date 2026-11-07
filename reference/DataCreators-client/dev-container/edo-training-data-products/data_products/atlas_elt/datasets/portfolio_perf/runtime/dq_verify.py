# Databricks notebook source

# COMMAND ----------

import logging

logger = logging.getLogger(__name__)

dbutils.widgets.text("application_name", "edo-training-data-products")
dbutils.widgets.text("dataset_name", "atlas_portfolio_perf_base")
dbutils.widgets.text("ruleset_name", "atlas_portfolio_perf_base")
dbutils.widgets.text("rule_group", "Daily")
dbutils.widgets.text("env", "dev1")
dbutils.widgets.text("schema", "")
dbutils.widgets.text("table", "rpt_portfolio_performance")

application_name = dbutils.widgets.get("application_name")
dataset_name = dbutils.widgets.get("dataset_name")
ruleset_name = dbutils.widgets.get("ruleset_name")
rule_group = dbutils.widgets.get("rule_group")

if not dataset_name:
    raise ValueError("'dataset_name' is required and cannot be empty")
if not ruleset_name:
    raise ValueError("'ruleset_name' is required and cannot be empty")

logger.info(
    "DQ placeholder ready - app: %s, dataset: %s, ruleset: %s, rule_group: %s",
    application_name,
    dataset_name,
    ruleset_name,
    rule_group,
)
