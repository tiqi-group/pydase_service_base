from __future__ import annotations

import datetime
import json
import logging
import re
from typing import TYPE_CHECKING, Any

try:
    from typing import Self  # type: ignore
except ImportError:
    from typing_extensions import Self

from confz import FileSource
from dateutil.parser import ParserError, parse  # type: ignore
from sqlmodel import Session, SQLModel, create_engine

from pydase_service_base.database.config import (
    OperationMode,
    PostgreSQLConfig,
    ServiceConfig,
)

if TYPE_CHECKING:
    from pathlib import Path
    from types import TracebackType

logger = logging.getLogger(__name__)


def json_loads_or_return_input(input_string: str) -> dict[str, Any] | Any:
    """
    Try to parse a string as JSON, if it fails return the original string.
    """
    try:
        return json.loads(input_string)
    except (TypeError, json.JSONDecodeError):
        return input_string


def parse_datetime_or_return_str(input_string: str) -> datetime.datetime | str:
    try:
        # Attempts to parse the string as a datetime object
        return parse(input_string)
    except ParserError:
        # If parsing fails, return the original input string
        return input_string


def is_datetime_format(input_string: str) -> bool:
    """
    Check if a string is in datetime format.
    """
    try:
        parse(input_string)
        return True
    except ParserError:
        return False


def json_dumps(data: Any) -> str | list[Any]:
    """
    Serialize a Python object into a JSON-formatted string, with custom handling for
    datetime and list objects.
    """
    # 'Infinity' is an unallowed token in JSON, thus make it a string
    # https://stackoverflow.com/questions/48356938/store-infinity-in-postgres-json-via-django
    pattern = r"(-?Infinity)"
    result: str | list[Any]

    if isinstance(data, str):
        result = json.dumps(data) if is_datetime_format(data) else data
    elif isinstance(data, datetime.datetime):
        result = json.dumps(str(data))
    elif isinstance(data, list):
        result = [json_dumps(element) for element in data]
    else:
        if isinstance(data, SQLModel):
            serialized_data = data.json()
        else:
            serialized_data = json.dumps(data)
        result = re.sub(pattern, r'"\1"', serialized_data)
    return result


def deserialize_json_dict(json_string: str) -> Any:
    """
    Deserialize a JSON string into a Python dictionary.
    """
    # 'Infinity' is an unallowed token in JSON, thus we made it a string. Now, convert
    # it back
    pattern = r'"(-?Infinity)"'
    json_string = re.sub(pattern, r"\1", json_string)
    result: Any

    val = json.loads(json_string)
    json_dict_or_val = json_loads_or_return_input(val)
    if isinstance(json_dict_or_val, str):
        result = parse_datetime_or_return_str(json_dict_or_val)
    else:
        result = json_dict_or_val
    return result


class PostgresDatabaseSession(Session):
    """A class to represent a session with the PostgreSQL database.

    This class inherits from SQLModel's Session class and implements Python's context
    manager protocol. This class helps to ensure that sessions are properly opened
    and closed, even in cases of error.

    The main goal of this class is to provide a way to manage persistence operations
    for ORM-mapped objects.

    Attributes:
        bind: Represents the database engine to which this session is bound.

    Example:
        This class is designed to be used with a context manager (the 'with' keyword).
        Here's how you can use it to query data from a table represented by a SQLModel
        class named 'YourModel':

        ```python
        from your_module.models import YourModel  # replace with your model
        from sqlmodel import select

        with PostgresDatabaseSession() as session:
            row = session.exec(select(YourModel).limit(1)).all()
        ```

        You can also use it to add new data to the table:

        ```python
        with PostgresDatabaseSession() as session:
            new_row = YourModel(...)  # replace ... with your data
            session.add(new_row)
            session.commit()
        ```
    """

    conf_folder: Path | str

    def __init__(self) -> None:
        """Initializes a new session bound to the database engine."""
        self._config = PostgreSQLConfig(
            config_sources=FileSource(
                ServiceConfig().database_config_dir
                / f"postgres_{OperationMode().environment}.yaml"
            )
        )

        super().__init__(
            bind=create_engine(
                f"postgresql://{self._config.user}:{self._config.password}@"
                f"{self._config.host.host}:{self._config.port}/"
                f"{self._config.database}",
                echo=False,
                json_serializer=json_dumps,
                json_deserializer=deserialize_json_dict,
            )
        )

    def __enter__(self) -> Self:
        """Begins the runtime context related to the database session."""

        super().__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        exc_traceback: TracebackType | None,
    ) -> None:
        """Ends the runtime context related to the database session.

        Ensures that the session is properly closed, even in the case of an error.
        """

        super().__exit__(exc_type, exc_value, exc_traceback)
