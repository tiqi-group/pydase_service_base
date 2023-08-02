# ICON Service Base

ICON Service Base is a shared code repository for Icon services in a service-based architecture. It is written in Python and provides functionality for interacting with PostgreSQL and InfluxDB v2 databases.

## Installation

Make sure you have Python 3.10 or later installed on your system. The dependencies of this package are handled with [`poetry`](https://python-poetry.org/docs/#installation). You can install the `icon_service_base` like so:

```bash
poetry add git+ssh://git@gitlab.phys.ethz.ch:tiqi-projects/qchub/icon-services/icon_service_base.git
```

## Configuration

The database connections are managed using configurations provided through environment variables or a configuration file.

The package expects a `database_config` folder in the root directory of any module installing this package, which should contain the configuration files for the databases. The location of the `database_config` folder can be overridden by passing a different path to the constructor of the database classes.

The `database_config` folder should have the following structure:

```
database_config
├── influxdb_config.yaml
├── postgres_development.yaml
└── postgres_production.yaml
```

Here is an example of the contents of the configuration files:

`influxdb_config.yaml`:

```yaml
url: https://database-url.ch
org: your-org
token: <influxdb-token>
```

`postgres_development.yaml` / `postgres_production.yaml`:

```yaml
database: ...
host: https://database-url.ch
port: 5432
password: ...
user: ...
```

## Usage

### InfluxDBSession

You can use the `InfluxDBSession` class to interact with an InfluxDB server. **Please note that this class only supports InfluxDB v2**.

```python
from icon_service_base.database import InfluxDBSession

with InfluxDBSession() as influx_client:
    # Creating a bucket
    influx_client.create_bucket(
        bucket_name='my_new_bucket', description='This is a new bucket'
    )

    # Writing data to a bucket
    record = {
        "measurement": "your_measurement",  # Replace with your measurement
        "tags": {
            "example_tag": "tag_value",  # Replace with your tag and its value
        },
        "fields": {
            "example_field": 123,  # Replace with your field and its value
        },
        "time": "2023-06-05T00:00:00Z",  # Replace with your timestamp
    }
    influx_client.write_api.write(
        bucket='my_new_bucket', record=record
    )
```

### PostgresDatabaseSession

The `PostgresDatabaseSession` class can be used to interact with a PostgreSQL database. Here's an example of how to use it:

```python
from icon_service_base.database import PostgresDatabaseSession
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

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.