from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .influxdb_session import InfluxDBSession  # type: ignore
    from .influxdbv1_session import InfluxDBv1Session  # type: ignore
    from .influxdbv3_session import InfluxDBv3Session  # type: ignore
    from .postgres_session import PostgresDatabaseSession  # type: ignore
else:

    class OptionalDependencyError(Exception):
        """Exception raised when an optional dependency is not installed."""

    try:
        import influxdb_client  # type: ignore # noqa

        from .influxdb_session import InfluxDBSession  # type: ignore
    except ImportError:

        class InfluxDBSession:  # type: ignore
            def __init__(self) -> None:
                raise OptionalDependencyError(
                    "InfluxDBSession requires the 'influxdbv2' extra. "
                    "Please refer to https://gitlab.phys.ethz.ch/tiqi-projects/qchub/icon-services/pydase_service_base."
                )

    try:
        import influxdb  # type: ignore # noqa

        from .influxdbv1_session import InfluxDBv1Session  # type: ignore
    except ImportError:

        class InfluxDBv1Session:  # type: ignore
            def __init__(self) -> None:
                raise OptionalDependencyError(
                    "InfluxDBv1Session requires the 'influxdbv1' extra. "
                    "Please refer to https://gitlab.phys.ethz.ch/tiqi-projects/qchub/icon-services/pydase_service_base."
                )
    try:
        import influxdb_client_3  # type: ignore # noqa

        from .influxdbv3_session import InfluxDBv3Session  # type: ignore
    except ImportError:

        class InfluxDBv3Session:  # type: ignore
            def __init__(self) -> None:
                raise OptionalDependencyError(
                    "InfluxDBv3Session requires the 'influxdbv3' extra. "
                    "Please refer to https://gitlab.phys.ethz.ch/tiqi-projects/qchub/icon-services/pydase_service_base."
                )
    try:
        import sqlmodel  # noqa

        from .postgres_session import PostgresDatabaseSession  # type: ignore
    except ImportError:

        class PostgresDatabaseSession:  # type: ignore
            def __init__(self) -> None:
                raise OptionalDependencyError(
                    "PostgresDatabaseSession requires the 'postgresql' extra. "
                    "Please refer to https://gitlab.phys.ethz.ch/tiqi-projects/qchub/icon-services/pydase_service_base."
                )


__all__ = ["InfluxDBSession", "InfluxDBv1Session", "InfluxDBv3Session", "PostgresDatabaseSession"]
