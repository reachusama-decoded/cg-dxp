import typing
import datetime
from caspian.curation.spark.spark_helpers import escape_sql_literal


class AuditingColumn:
    def __init__(self,
                 name: str,
                 provider: typing.Union[typing.Callable[[], typing.Any], typing.Any],
                 aliases: typing.Tuple[str, ...] = ()):
        """
        Auditing Column objet to define a well known audit column
        :param name: preferred name of auditing column;
        :param provider: value provider for audit column. Return value will be static
        :param aliases: Aliases of the audit column name. You may specify the legacy audit column names
        """
        self.name = name
        self.provider_or_value = provider
        self.aliases = aliases

    def set_provider(self, provider: typing.Callable[[], typing.Any]):
        """
        Set the provider for the column
        :param provider: provider function
        """
        self.provider_or_value = provider

    def matched_in(self, candidates: typing.List[str]) -> typing.Optional[str]:
        """
        If this column is matched by one of candidate column. It will return the matched column name. During
        name matching, case of column is ignored (a.k.a. case-insensitive match).
        :param candidates: candidate columns
        :return: matched column if found; else None
        """
        for alias in [self.name, *self.aliases]:
            # Base on the assumptions that audit columns are always in last
            for c in reversed(candidates):
                if alias.lower() == c.lower():
                    return c
        return None

    def as_sql_text_expr(self) -> str:
        """
        :return: The SQL compatible expression to denote the expression.
        """
        val = self.as_value()
        return escape_sql_literal(val) if val is not None else 'null'

    def as_value(self) -> typing.Any:
        """
        :return: The value. Invoke the provider
        """
        return self.provider_or_value() if callable(self.provider_or_value) else self.provider_or_value


class StandardAuditColumns:
    """
    This class define the standard auditing columns. Below are the defined preferred column names. AS of now no aliases
    are defined. This value can be populated based on requirements.
    """
    SYS_CREATED = AuditingColumn("sys_created", datetime.datetime.utcnow(), ("dlloadtimestamp",))
    SYS_UPDATED = AuditingColumn("sys_updated", datetime.datetime.utcnow(), ("dllastupdatetimestamp",))
    SYS_PROCESS_NAME = AuditingColumn("sys_process_name", "",
                                      ("dllastupdateprocessid", "dl_last_update_process_id"))

    @classmethod
    def matched_columns(cls, candidates: typing.List[str], run_id) -> typing.Dict[str, AuditingColumn]:
        """
        Try to determine the standard audit columns based on the given list.
        :param run_id:
        :param candidates: column names
        :return: Mapping of matched audit columns and audit column object
        """
        cls.SYS_PROCESS_NAME.set_provider(run_id)
        matched = {}
        for audit_col in [getattr(cls, c) for c in dir(cls) if isinstance(getattr(cls, c), AuditingColumn)]:
            found = audit_col.matched_in(candidates)
            if found:
                matched[found] = audit_col
        return matched


def match_standard_audit_columns(target_columns: typing.List[str], run_id) -> typing.Dict[str, AuditingColumn]:
    return StandardAuditColumns.matched_columns(target_columns, run_id)


def generate_audit_columns_for_dbt(audits: typing.Dict[str, AuditingColumn]) -> str:
    audit_cols_list = []

    for c, column in audits.items():
        audit_cols_list.append(f"'{str(column.as_value())}' as {c}")
    audit_cols_str = ','.join(audit_cols_list)

    return audit_cols_str
