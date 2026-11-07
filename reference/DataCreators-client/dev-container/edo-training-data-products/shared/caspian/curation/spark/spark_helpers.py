import typing

from caspian.curation import exceptions, miscutils


def sql_quote(name: str) -> str:
    return f"`{name}`"


def sql_text_safe_fqn(qualifier: typing.Optional[str], name: str) -> str:
    if not qualifier:
        return f"`{name}`"

    qualifier_parts = [p for p in qualifier.split('.') if p]
    all_parts = qualifier_parts + [name]
    return '.'.join(f"`{part}`" for part in all_parts)


def escape_sql_literal(value: str):
    """
    :param value: value to be escaped
    :return: escaped value
    """
    if value is None:
        return None

    if isinstance(value, int):
        return f"{value}"
    if value:
        value = value.strip()
    if "`" in value:
        value = value.replace("`", "")
    if "'" in value:
        value = value.replace("'", "''")

    return f"'{value}'"


class PartitionKey:
    def __init__(self, keys: typing.List[str], values: typing.List[typing.Any]):
        self.keys = keys
        self.values = values
        self.cmp_value = tuple(values)

    def __lt__(self, other):
        return self.cmp_value < other.cmp_value

    def __repr__(self):
        return "/".join([f"{k}={v}" for k, v in zip(self.keys, self.values)])

    def to_sql_filter_expr(self):
        return f"{self.to_sql_filter_expr_keys()} = {self.to_sql_filter_expr_values()}"

    def to_sql_filter_expr_keys(self):
        if len(self.keys) == 1:
            return sql_quote(self.keys[0])
        return f"({','.join([sql_quote(k) for k in self.keys])})"

    def to_sql_filter_expr_values(self):
        if len(self.values) == 1:
            return escape_sql_literal(self.values[0])
        return f"({','.join([escape_sql_literal(v) for v in self.values])})"


def get_table_location(exec_sql_, table_fqn: str) -> str:
    rows = exec_sql_(f"describe extended {table_fqn}")
    section = "#columns"
    for row in rows:
        col_name = row[0]
        data_type_or_val = row[1]
        if col_name and col_name[0] == '#':
            section = row[0]
            continue
        if section == "# Detailed Table Information":
            if col_name == 'Location':
                return data_type_or_val
    raise exceptions.IllegalArgumentException(f"Could not retrieve table's location: {table_fqn}")


class GeneralPartitionKeyBuilder:
    def __init__(self, keys_metadata: typing.Dict[str, typing.Dict[str, typing.Any]]):
        self._keys_metadata = keys_metadata

    def _get_field_type(self, field: str) -> typing.Type:
        meta_ = self._keys_metadata.get(field)
        miscutils.check_required_argument(meta_, f"partition field '{field}' is unknown")
        caster: typing.Type = meta_["caster"]

        return caster

    def parse(self, key: str) -> PartitionKey:
        parts = key.split("/")

        parts_names = []
        parts_values = []
        for c in parts:
            name, value = c.split('=', maxsplit=1)
            parts_names.append(name)
            parts_values.append(self._get_field_type(name)(value))

        return PartitionKey(parts_names, parts_values)
