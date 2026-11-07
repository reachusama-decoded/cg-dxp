from enum import Enum
import sys
from datacontract.export.exporter_factory import exporter_factory

# from: https://github.com/datacontract/datacontract-cli/blob/main/datacontract/export/exporter.py
# Register new exporters to the function
class ExportFormat(str, Enum):
    # these are the default exporters. add new exporters here from upstream.
    jsonschema = "jsonschema"
    pydantic_model = "pydantic-model"
    sodacl = "sodacl"
    dbt = "dbt"
    dbt_sources = "dbt-sources"
    dbt_staging_sql = "dbt-staging-sql"
    odcs = "odcs"
    rdf = "rdf"
    avro = "avro"
    protobuf = "protobuf"
    great_expectations = "great-expectations"
    avro_idl = "avro-idl"
    sql = "sql"
    sql_query = "sql-query"
    mermaid = "mermaid"
    html = "html"
    go = "go"
    bigquery = "bigquery"
    dbml = "dbml"
    spark = "spark"
    sqlalchemy = "sqlalchemy"
    data_caterer = "data-caterer"
    dcs = "dcs"
    markdown = "markdown"
    iceberg = "iceberg"
    custom = "custom"
    excel = "excel"
    dqx = "dqx"

    # add custom exporters here.
    dbsql = "dbsql"

    @classmethod
    def get_supported_formats(cls):
        return list(map(lambda c: c.value, cls))

sys.modules["datacontract.export.exporter"].ExportFormat = ExportFormat


# from: https://github.com/datacontract/datacontract-cli/blob/main/datacontract/export/exporter_factory.py
# Register new Factories
exporter_factory.register_lazy_exporter(
    name=ExportFormat.dbsql,
    module_path="datacounsel.export.dbsql_exporter",
    class_name="DbSqlExporter",
)