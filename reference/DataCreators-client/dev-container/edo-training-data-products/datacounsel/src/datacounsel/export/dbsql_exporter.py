# Inspired by: https://github.com/datacontract/datacontract-cli/blob/main/datacontract/export/sql_exporter.py


from open_data_contract_standard.model import OpenDataContractStandard, SchemaObject
from datacontract.export.sql_type_converter import convert_to_sql_type
from datacontract.export.exporter import Exporter, _determine_sql_server_type
from datacontract.export.sql_exporter import _escape


# Patches to_sql_ddl to support external locations

class DbSqlExporter(Exporter):
    def export(self, data_contract, schema_name, server, sql_server_type, export_args) -> str:
        server_type = _determine_sql_server_type(
            data_contract,
            sql_server_type,
        )
        return to_sql_ddl(data_contract, server_type, export_args.get("server"))

def to_sql_ddl(
    data_contract: OpenDataContractStandard,
    server_type: str = "databricks",
    server: str = None,
    external: bool = False,
    data_product: str = "",
    deployment_mode: str = "databricks",
    location_path_override: str | None = None,
) -> str:
    if data_contract is None:
        return ""
    if data_contract.schema_ is None or len(data_contract.schema_) == 0:
        return ""

    # Always use Flyway placeholders — actual values injected at migrate time
    table_prefix = "${catalog}.${schema}."

    result = ""
    result += f"-- Data Contract: {data_contract.id}\n"
    result += f"-- SQL Dialect: {server_type}\n"

    for schema_obj in data_contract.schema_:
        # Read format from the schema object if present, default to delta
        table_format = getattr(schema_obj, "format", None) or "delta"

        if external:
            if deployment_mode == "emr":
                # EMR: ${emr_location}/{physicalName} — separate placeholder, no data_product prefix
                leaf = location_path_override or schema_obj.name
                table_location = f"${{emr_location}}/{leaf}"
            else:
                # Databricks (default): ${location}/${data_product}/<table_name>
                location_path = f"${{data_product}}/{schema_obj.name}" if data_product else schema_obj.name
                table_location = f"${{location}}/{location_path}"
        else:
            table_location = ""

        result += _to_sql_table(table_prefix + schema_obj.name, schema_obj, server_type, table_location, table_format)

    return result.strip()


def _to_sql_table(model_name: str, model: SchemaObject, server_type: str = "snowflake", table_location: str = None, table_format: str = None) -> str:
    if server_type == "databricks":
        result = f"CREATE TABLE IF NOT EXISTS {model_name} (\n"
    else:
        result = f"CREATE TABLE {model_name} (\n"

    properties = model.properties or []
    fields = len(properties)
    current_field_index = 1

    for prop in properties:
        type_str = convert_to_sql_type(prop, server_type)
        result += f"  {prop.name} {type_str}"
        if prop.required:
            result += " not null"
        if prop.primaryKey:
            result += " primary key"
        if server_type == "databricks" and prop.description is not None:
            result += f' COMMENT "{_escape(prop.description)}"'
        if server_type == "snowflake" and prop.description is not None:
            result += f" COMMENT '{_escape(prop.description)}'"
        if current_field_index < fields:
            result += ","
        result += "\n"
        current_field_index += 1
    result += ")\n"

    if table_format:
        result += f" USING {table_format}\n"

    # Add partition keys
    _partition_keys = {}
    for prop in properties:
        if prop.partitioned:
            if prop.partitionKeyPosition in _partition_keys:
                raise ValueError(
                    f"Partition keys {prop.name}, {_partition_keys[prop.partitionKeyPosition]} have the same partitionKeyPosition of {prop.partitionKeyPosition}"
                )
            _partition_keys[prop.partitionKeyPosition] = prop.name
    if _partition_keys:
        result += f" PARTITIONED BY ({', '.join([value for _, value in sorted(_partition_keys.items(), key=lambda item: item[0])])})\n"

    if table_location:
        result += f" LOCATION '{_escape(table_location)}'\n"

    if server_type == "databricks" and model.description is not None:
        result += f' COMMENT "{_escape(model.description)}"'
    if server_type == "snowflake" and model.description is not None:
        result += f" COMMENT='{_escape(model.description)}'"
    result += ";\n"
    return result
