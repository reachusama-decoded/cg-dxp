"""Miscellaneous  Utility functions"""
import collections
import contextlib
import datetime
import inspect
import io
import logging
import os
import pathlib
import re
import sys
import typing
import json

from caspian.curation import exceptions
from collections import OrderedDict
from collections.abc import Set

T = typing.TypeVar('T')

_FALSE_LIT = {False, 'False', 'false', 'FALSE',
              'None', 'none', 'NONE',
              'N', 'n',
              '0', '0.0',
              'no', 'No', 'NO',
              'Off', 'off', 'OFF', ''}


def to_bool(value: typing.Union[typing.Any]) -> bool:
    """
    Type Converter function to handle the nance in default boolean type converter and to support the human readable
    boolean expression.

    >>> to_bool('Off')
    False
    >>> to_bool('False')
    False
    """
    return bool(value) if value not in _FALSE_LIT else False


def log(level, msg, *args, **kwargs):
    """
    General logging when you don't have logger object.

    >>> log(logging.WARNING, "This is Warning Message")
    >>> log(logging.INFO, "This is Info Message")
    """
    frm = inspect.stack()[1]
    module = inspect.getmodule(frm[0])
    logger_name = module.__name__ if module else "caspian"

    logging.getLogger(logger_name).log(level, msg, *args, **kwargs)


def try_to_date(value: typing.Optional[str],
                formats: typing.Collection[str] = ("%Y-%m-%d", "%Y%m%d")) -> typing.Optional[datetime.date]:
    if value is None:
        return

    for f in formats:
        try:
            return datetime.datetime.strptime(value, f).date()
        except ValueError:
            pass

    raise ValueError(f"invalid date: '{value}'. (choose a format from {', '.join(formats)})")


@contextlib.contextmanager
def run_in_directory(d: typing.Union[str, pathlib.Path]):
    """
    >>> with run_in_directory(".."): print(f"Running in parent dir")
    Running in parent dir

    Execute a piece of code by changing current working directory to given directory.
    :param d: current working directory
    """
    prev_cwd = os.getcwd()
    os.chdir(d)
    try:
        yield
    finally:
        os.chdir(prev_cwd)


@contextlib.contextmanager
def capture_logger_statement(logger: typing.Union[str, logging.Logger]) -> io.StringIO:
    str_io = io.StringIO()
    lgr = logger if isinstance(logger, logging.Logger) else logging.getLogger(logger)

    hdlr = logging.StreamHandler(str_io)
    lgr.addHandler(hdlr)
    try:
        yield str_io
    finally:
        lgr.removeHandler(hdlr)


def read_text_file(path: str) -> str:
    with open(path, encoding="utf-8") as fp:
        text = fp.read()
    return text


def patch_yaml_data(yaml_content: str, **kwargs) -> str:
    """
    This utility function patches/updates the given yaml content with the passed key value pairs.
    :param yaml_content: valid Yaml Content
    :param kwargs: Updated Key value pairs which will be updated
    :raise parser_error yaml.error.YAMLError
    :return: Patched/Updated YAML content

    """
    import yaml
    from io import StringIO

    data = yaml.safe_load(yaml_content)
    data.update(**kwargs)

    with StringIO() as sink:
        yaml.safe_dump(data, sink)
        _patched = sink.getvalue()

    return _patched


def check_choice_argument(choice: typing.Any, choices: typing.Collection[typing.Any], name: str = None):
    """
    Validate given choice is one of the among choices.
    :param choice:
    :param choices:
    :param name:
    :return:
    """
    if choice not in choices:
        msg = f"{name or 'choice'} must be one of {choices} but it was: {choice}"
        raise exceptions.IllegalArgumentException(msg)


def check_required_argument(value: typing.Any, name: str = None):
    if value is None:
        msg = f"{name or 'value'} must not be none"
        raise exceptions.IllegalArgumentException(msg)


def check_conditional_argument(condition: bool, msg: str = None):
    if not condition:
        msg = msg or "condition failed"
        raise exceptions.IllegalArgumentException(msg)


def check_mutual_inclusive_arguments(a: typing.Any, b: typing.Any, msg: str = None):
    check_conditional_argument(not (a is None) ^ (b is None), msg)


def split_csv_line(v: str) -> list:
    return [x for x in [e.strip() for e in v.split(',')] if len(x) != 0] if v is not None else []


def coerce_as_list(o_or_l: typing.Union[typing.Any, typing.List[typing.Any]]) -> typing.List[typing.Any]:
    return o_or_l if isinstance(o_or_l, list) else o_or_l if o_or_l is None else [o_or_l]


def excludes_ignore_case(candidates: typing.Sequence[str], excludes: typing.Sequence[str]):
    lower_excludes = {c.lower() for c in excludes}
    return [c for c in candidates if c.lower() not in lower_excludes]


def find_first_index(candidates: typing.List[typing.Any], match: typing.Callable[[typing.Any], bool]) -> int:
    for i, item in enumerate(candidates):
        if match(item):
            return i
    return -1


def find_first_item(candidates: typing.List[typing.Any], match: typing.Callable[[typing.Any], bool]) -> typing.Any:
    for i, item in enumerate(candidates):
        if match(item):
            return item
    return None


def contains_ignore_case(candidates: typing.List[str], search: str) -> bool:
    return any([c.lower() == search.lower() for c in candidates])


__TO_SNAKE_CASE = re.compile(r'((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')


def as_snake_case_identifier(name: str):
    return __TO_SNAKE_CASE.sub(r'_\1', name).lower()


def first_or_none(source: typing.List[T]) -> T:
    # source should be a list of any type
    return source[0] if source is not None and len(source) >= 1 else None


def last_or_none(source: typing.List[T]) -> T:
    # source should be a list of any type
    return source[-1:][0] if source is not None and len(source) >= 1 else None


class ValueRef:
    def __init__(self, value: T = None):
        self.value = value


class OrderedSet(Set):
    def __init__(self, iterable=()):
        self.d = collections.OrderedDict.fromkeys(iterable)

    def __len__(self):
        return len(self.d)

    def __contains__(self, element):
        return element in self.d

    def __iter__(self):
        return iter(self.d)


class CurrentPipelineMetricsProvider:
    _metrics = OrderedDict()

    @classmethod
    def get(cls, name: str) -> typing.Any:
        return cls._metrics.get(name)

    @classmethod
    def pop(cls, name: str) -> typing.Any:
        return cls._metrics.pop(name)

    @classmethod
    def items(cls) -> typing.ItemsView[str, typing.Any]:
        return cls._metrics.items()

    @classmethod
    def put(cls, name: str, value: typing.Any):
        cls._metrics[name] = value


def add_metric(name: str, value: typing.Any):
    CurrentPipelineMetricsProvider.put(name, value)


def get_metric(name: str):
    return CurrentPipelineMetricsProvider.get(name)


def pop_metric(name: str):
    return CurrentPipelineMetricsProvider.pop(name)


def get_all_metrics():
    return CurrentPipelineMetricsProvider.items()


def set_return_values(values):
    """
    Writes the provided values to a JSON file in the specified path for XCom compatibility.
    The XCom path is retrieved dynamically from the XCOM_PATH environment variable or defaults to
    '/Workspace/Shared/_platform/airflow/xcom/return.json'.
    """
    # Retrieve the XCOM_PATH environment variable or use a default value
    xcom_path = os.getenv("XCOM_PATH")
    print(f"XCom path: {xcom_path}")
    
    try:
        # Ensure the directory exists
        directory = os.path.dirname(xcom_path)
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"Directory created: {directory}")
        else:
            print(f"Directory already exists: {directory}")

        # Write the JSON content to the specified file
        with open(xcom_path, "w", encoding="utf-8") as f:
            json.dump(values, f, ensure_ascii=False, indent=4)
        print(f"XCom file written to {xcom_path}")
    except Exception as e:
        print(f"Failed to write XCom file: {e}")

@contextlib.contextmanager
def sys_args(argv):
    orig_sys_argv = sys.argv
    try:
        sys.argv = argv
        yield
    finally:
        sys.argv = orig_sys_argv


def pairwise(seq):
    for i in range(0, len(seq), 2):
        yield seq[i], seq[i + 1]


def removeprefix(value: str, prefix: str):
    if value.startswith(prefix):
        value = value[len(prefix):]
    return value
