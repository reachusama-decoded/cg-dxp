import re
import yaml
from datetime import datetime, timezone
from pathlib import Path

from open_data_contract_standard.model import OpenDataContractStandard
from datacontract.export.sql_type_converter import convert_to_sql_type
from datacontract.export.sql_exporter import _escape

from .export.dbsql_exporter import to_sql_ddl


def generate_migration(
    contract_path: str,
    output_dir: str = "migrations",
) -> list[Path]:
    """Generate Flyway versioned migration SQL files from an ODCS contract.

    - First migration for a table: emits one CREATE TABLE file.
    - Subsequent migrations: diffs prior SQL files and emits one file per atomic DDL change.
      Multiple changes produce sub-versioned files (V1.0.7.1__, V1.0.7.2__, etc.) so each
      file contains exactly one statement — making each migration effectively atomic on
      non-transactional databases like Databricks.

    Returns a list of Paths to the generated migration files.
    """
    contract_path = Path(contract_path)

    with open(contract_path) as f:
        raw = yaml.safe_load(f)

    # Validate it looks like an ODCS contract
    if raw.get("kind") != "DataContract" or "apiVersion" not in raw:
        raise ValueError(
            f"{contract_path} does not appear to be an ODCS contract (expected kind=DataContract). "
            "Use the .odcs.yaml file, not the .datacontract.yaml file."
        )

    version: str = raw.get("version", "0.0.0")
    # Version tag used in filenames — dots replaced with underscores so Flyway doesn't
    # interpret them as sub-version separators (e.g. "1.0.3" → "1_0_3")
    version_tag: str = version.replace(".", "_")

    schema_entries = raw.get("schema", [])
    if not schema_entries:
        raise ValueError(f"No schema entries found in contract: {contract_path}")

    # name = external table name (never has _v4 suffix)
    # physicalName = S3 storage path leaf (may differ, e.g. geography_v4)
    table_name: str = schema_entries[0].get("name")
    physical_name: str = schema_entries[0].get("physicalName") or table_name
    if not table_name:
        raise ValueError(f"Could not determine table name from schema in: {contract_path}")

    # Read grants and external flag before validation — not in ODCS spec
    select_grants: list[str] = raw.get("grants", {}).get("select", [])
    is_external: bool = bool(schema_entries[0].get("external", False))

    # Read deployment config — controls EMR vs Databricks DDL generation
    deployment: dict = raw.get("deployment", {})
    deployment_mode: str = deployment.get("mode", "databricks")
    # In EMR mode, use physicalName as the S3 leaf path (e.g. geography_v4)
    location_path_override: str | None = physical_name if physical_name != table_name else None

    # Extract data product name from contract path: data_products/{data_product}/...
    # Used to scope the external table location: ${location}/{data_product}/{table_name}
    _parts = contract_path.parts
    _dp_index = next((i for i, p in enumerate(_parts) if p == "data_products"), None)
    data_product: str = _parts[_dp_index + 1] if _dp_index is not None and _dp_index + 1 < len(_parts) else ""

    # Strip non-ODCS fields from schema entries and top-level before model validation
    def _strip_extra(entry: dict) -> dict:
        return {k: v for k, v in entry.items() if k not in ("format", "external")}

    cleaned = {k: v for k, v in raw.items() if k not in ("grants", "deployment")}
    cleaned["schema"] = [_strip_extra(e) for e in cleaned.get("schema", [])]
    odcs = OpenDataContractStandard.model_validate(cleaned)

    # Always use Flyway placeholders — catalog/schema injected at migrate time
    contract_table_name = f"${{catalog}}.${{schema}}.{table_name}"

    # Write directly to output_dir — no server/schema subdirectory.
    # The caller (contract:migrate) is responsible for pointing output_dir at
    # flyway/migrations/<data_product>/, which IS the schema-scoped folder.
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Find any prior migration files for this table (sorted chronologically by timestamp prefix)
    prior_files = sorted(output_path.glob(f"V*__{table_name}_v*.sql"))

    # Refuse to overwrite existing files for this version — corrupts Flyway checksums
    existing = sorted(output_path.glob(f"V*__{table_name}_v{version_tag}.sql"))
    if existing:
        raise FileExistsError(
            f"Migration files already exist for version {version}: {[str(f) for f in existing]}\n"
            "Overwriting applied migrations corrupts Flyway's checksum history. "
            "Bump the contract version to apply schema changes."
        )

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")

    if not prior_files:
        # Initial migration — full CREATE TABLE
        filename = f"V{timestamp}__{table_name}_v{version_tag}.sql"
        migration_file = output_path / filename
        ddl = to_sql_ddl(
            odcs,
            server_type="databricks",
            external=is_external,
            data_product=data_product,
            deployment_mode=deployment_mode,
            location_path_override=location_path_override,
        )
        grant_sql = _generate_grant_statements(contract_table_name, select_grants)
        migration_file.write_text(ddl + "\n" + grant_sql)
        return [migration_file]
    else:
        # Incremental migration — one file per atomic DDL change
        prev_columns = _parse_existing_columns(prior_files)
        prev_location = _parse_existing_location(prior_files)
        prev_grants = _parse_existing_grants(prior_files)

        if not is_external:
            new_location = None
        elif deployment_mode == "emr":
            leaf = location_path_override or table_name
            new_location = f"${{emr_location}}/{leaf}"
        else:
            new_location = f"${{location}}/${{data_product}}/{table_name}"

        full_table_name = _parse_full_table_name(prior_files[0])
        statements = _generate_alter_statements(
            full_table_name=full_table_name,
            prev_columns=prev_columns,
            prev_location=prev_location,
            prev_grants=prev_grants,
            new_grants=select_grants,
            new_location=new_location,
            schema_obj=odcs.schema_[0],
            contract_id=raw.get("id", str(contract_path)),
            version=version,
        )
        if len(statements) == 1:
            # Single change — no sub-version needed
            filename = f"V{timestamp}__{table_name}_v{version_tag}.sql"
            f = output_path / filename
            f.write_text(statements[0])
            return [f]
        else:
            # Multiple changes — sub-version each so Flyway applies them as separate transactions
            files = []
            for i, stmt_content in enumerate(statements, 1):
                filename = f"V{timestamp}.{i}__{table_name}_v{version_tag}.sql"
                f = output_path / filename
                f.write_text(stmt_content)
                files.append(f)
            return files


def _parse_full_table_name(first_migration: Path) -> str:
    """Extract the fully-qualified table name from the CREATE TABLE statement."""
    sql = first_migration.read_text()
    m = re.search(r"CREATE TABLE(?:\s+IF NOT EXISTS)?\s+(\S+)\s*\(", sql, re.IGNORECASE)
    if not m:
        raise ValueError(
            f"Could not parse table name from existing migration: {first_migration}"
        )
    return m.group(1)


def _parse_existing_columns(migration_files: list[Path]) -> dict[str, str]:
    """Replay prior migration files to derive the current column state.

    Returns {col_name_lower: SQL_TYPE_UPPER}.
    Handles CREATE TABLE column blocks and ALTER TABLE ADD/ALTER COLUMN statements.
    """
    columns: dict[str, str] = {}

    for f in migration_files:
        sql = f.read_text()

        # Parse column block from CREATE TABLE ... (\n  col TYPE,\n ...\n)
        in_columns = False
        for line in sql.splitlines():
            stripped = line.strip()
            if re.match(r"CREATE TABLE(?:\s+IF NOT EXISTS)?\s+\S+\s*\(", stripped, re.IGNORECASE):
                in_columns = True
                continue
            if in_columns:
                if stripped.startswith(")"):
                    in_columns = False
                    continue
                col_line = stripped.rstrip(",")
                m = re.match(r"^(\w+)\s+(\S+)", col_line)
                if m:
                    columns[m.group(1).lower()] = m.group(2).upper()

        # ALTER TABLE ... ADD COLUMN col TYPE
        for m in re.finditer(
            r"ALTER TABLE\s+\S+\s+ADD COLUMN\s+(\w+)\s+(\S+)", sql, re.IGNORECASE
        ):
            columns[m.group(1).lower()] = m.group(2).upper()

        # ALTER TABLE ... ALTER COLUMN col TYPE new_type
        for m in re.finditer(
            r"ALTER TABLE\s+\S+\s+ALTER COLUMN\s+(\w+)\s+TYPE\s+(\S+)", sql, re.IGNORECASE
        ):
            columns[m.group(1).lower()] = m.group(2).upper()

        # ALTER TABLE ... DROP COLUMN col
        for m in re.finditer(
            r"ALTER TABLE\s+\S+\s+DROP COLUMN\s+(\w+)", sql, re.IGNORECASE
        ):
            columns.pop(m.group(1).lower(), None)

    return columns


def _parse_existing_grants(migration_files: list[Path]) -> set[str]:
    """Collect all grantees from prior GRANT SELECT statements across migration files."""
    grantees: set[str] = set()
    for f in migration_files:
        sql = f.read_text()
        for m in re.finditer(r"GRANT SELECT ON TABLE\s+\S+\s+TO\s+`([^`]+)`", sql, re.IGNORECASE):
            grantees.add(m.group(1))
        for m in re.finditer(r"REVOKE SELECT ON TABLE\s+\S+\s+FROM\s+`([^`]+)`", sql, re.IGNORECASE):
            grantees.discard(m.group(1))
    return grantees


def _parse_existing_location(migration_files: list[Path]) -> str | None:
    """Extract the LOCATION from prior CREATE TABLE or SET LOCATION migrations, if present."""
    location = None
    for f in migration_files:
        sql = f.read_text()
        # SET LOCATION takes precedence (most recent)
        m = re.search(r"ALTER TABLE\s+\S+\s+SET LOCATION\s+'([^']+)'", sql, re.IGNORECASE)
        if m:
            location = m.group(1)
            continue
        # CREATE TABLE ... LOCATION
        m = re.search(r"LOCATION\s+'([^']+)'", sql, re.IGNORECASE)
        if m:
            location = m.group(1)
    return location


def _generate_alter_statements(
    full_table_name: str,
    prev_columns: dict[str, str],
    schema_obj,
    contract_id: str,
    version: str,
    prev_location: str | None = None,
    new_location: str | None = None,
    prev_grants: set[str] | None = None,
    new_grants: list[str] | None = None,
) -> list[str]:
    """Return one SQL file content string per atomic DDL change.

    Each string is a complete file (with header comments) containing exactly one statement.
    For DROP COLUMN migrations, a prerequisite SET TBLPROPERTIES file is prepended.
    Ordering: TBLPROPERTIES (if drops), ADD COLUMNs, ALTER COLUMN TYPEs, DROP COLUMNs, SET LOCATION.
    """
    header = (
        f"-- Data Contract: {contract_id}\n"
        f"-- Version: {version}\n"
        "-- SQL Dialect: databricks\n"
    )

    new_props_list = [(p.name.lower(), p) for p in (schema_obj.properties or [])]
    new_props = dict(new_props_list)

    added = []  # (prop, type_str, after_col_or_none)
    type_changed = []
    removed = [name for name in prev_columns if name not in new_props]
    location_changed = new_location and new_location != prev_location

    for i, (name, prop) in enumerate(new_props_list):
        new_type = convert_to_sql_type(prop, "databricks").upper()
        if name not in prev_columns:
            # Find the closest preceding column that already exists in the table
            after_col = None
            for j in range(i - 1, -1, -1):
                preceding_name = new_props_list[j][0]
                if preceding_name in prev_columns:
                    after_col = preceding_name
                    break
            added.append((prop, new_type, after_col))
        elif new_type != prev_columns[name]:
            type_changed.append((prop, new_type))

    if not added and not type_changed and not removed and not location_changed:
        return [header + "-- No schema changes detected in this version.\n"]

    statements = []

    # Enable column mapping first if any drops (Delta requirement — must precede DROP COLUMN)
    if removed:
        statements.append(
            header
            + f"ALTER TABLE {full_table_name} SET TBLPROPERTIES ('delta.columnMapping.mode' = 'name');\n"
        )

    for prop, type_str, after_col in added:
        stmt = f"ALTER TABLE {full_table_name} ADD COLUMN {prop.name} {type_str}"
        if prop.required:
            stmt += " NOT NULL"
        if prop.description:
            stmt += f' COMMENT "{_escape(prop.description)}"'
        if after_col:
            stmt += f" AFTER {after_col}"
        else:
            stmt += " FIRST"
        statements.append(header + stmt + ";\n")

    for prop, new_type in type_changed:
        statements.append(
            header + f"ALTER TABLE {full_table_name} ALTER COLUMN {prop.name} TYPE {new_type};\n"
        )

    for name in removed:
        statements.append(
            header + f"ALTER TABLE {full_table_name} DROP COLUMN {name};\n"
        )

    if location_changed:
        statements.append(
            header + f"ALTER TABLE {full_table_name} SET LOCATION '{new_location}';\n"
        )

    prev_grants_set = prev_grants or set()
    new_grants_set = set(new_grants or [])
    for grantee in sorted(new_grants_set - prev_grants_set):
        statements.append(
            header + f"GRANT SELECT ON TABLE {full_table_name} TO `{grantee}`;\n"
        )
    for grantee in sorted(prev_grants_set - new_grants_set):
        statements.append(
            header + f"REVOKE SELECT ON TABLE {full_table_name} FROM `{grantee}`;\n"
        )

    return statements


def _generate_grant_statements(full_table_name: str, select_grantees: list[str]) -> str:
    """Generate GRANT SELECT ON TABLE statements for each grantee."""
    if not select_grantees:
        return ""
    lines = [f"GRANT SELECT ON TABLE {full_table_name} TO `{g}`;" for g in select_grantees]
    return "\n".join(lines) + "\n"
