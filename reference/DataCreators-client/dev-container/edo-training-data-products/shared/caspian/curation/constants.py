import enum
import typing

from caspian.curation import exceptions, miscutils

GenericSQLExecWithTupleResults = typing.Callable[[str], typing.Optional[typing.List[typing.Tuple[typing.Any, ...]]]]


class DatasetLoadType(enum.Enum):
    dynamic = "dynamic"
    incremental = "incremental"
    full = "full"

    @classmethod
    def parse(cls, value: typing.Optional[str]) -> 'DatasetLoadType':
        if value is None:
            value = "dynamic"

        if isinstance(value, DatasetLoadType):
            return value

        try:
            return cls[value]
        except KeyError:
            raise exceptions.IllegalArgumentException(f"invalid data_set load type was specified: '{value}'")

    @classmethod
    def from_config(cls, config: typing.Dict[str, typing.Any]):
        key = miscutils.as_snake_case_identifier(cls.__name__)
        return cls.parse(config.get(key))


class DatasetLoadCatchupStrategy(enum.Enum):
    latest = "latest"
    chronological = "chronological"
    combined = "combined"

    @classmethod
    def parse(cls, value: typing.Optional[str]) -> typing.Optional['DatasetLoadCatchupStrategy']:
        if value is None or isinstance(value, DatasetLoadCatchupStrategy):
            return value
        try:
            return cls[value]
        except KeyError:
            raise exceptions.IllegalArgumentException(f"invalid data catchup strategy was specified: '{value}'")

    @classmethod
    def from_config(cls, config: typing.Dict[str, typing.Any]):
        key = miscutils.as_snake_case_identifier(cls.__name__)
        return cls.parse(config.get(key))


def read_load_type_and_catch_up_strategy(meta: typing.Dict[str, typing.Any]) -> \
        typing.Tuple[DatasetLoadType, DatasetLoadCatchupStrategy]:
    load_type = DatasetLoadType.from_config(meta)
    strategy = DatasetLoadCatchupStrategy.from_config(meta)

    if strategy is None:
        if load_type == DatasetLoadType.incremental:
            strategy = DatasetLoadCatchupStrategy.chronological
        elif load_type == DatasetLoadType.full:
            strategy = DatasetLoadCatchupStrategy.latest
    else:
        msg = f"{load_type} and {strategy} cannot be specified together. Please use different combinations"
        miscutils.check_conditional_argument(not (strategy == DatasetLoadCatchupStrategy.latest and  # noqa: W504
                                                  load_type == DatasetLoadType.incremental), msg)
    return load_type, strategy
