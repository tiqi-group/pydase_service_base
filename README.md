# `pydase` Service Base

`pydase` Service Base is a shared code repository for `pydase` services in a service-based architecture. Written in Python, it provides the essential functionality for interacting with PostgreSQL and InfluxDB v2 databases. In addition, it offers the `Ionizer Interface`, enabling seamless integration between `pydase` applications and the Ionizer system.

## Installation

Ensure you have Python 3.10 or later installed on your system. Dependencies of this package are managed with [`poetry`](https://python-poetry.org/docs/#installation). Install the `pydase_service_base` as follows:

```bash
poetry add git+https://github.com/tiqi-group/pydase_service_base.git
```

To utilize specific functionalities such as `IonizerServer`, `InfluxDBv1Session`,`InfluxDBSession`, or `PostgresDatabaseSession`, you need to install the relevant optional dependencies:

- For `IonizerServer`, include the `ionizer` extra:
  ```bash
  poetry add "git+https://github.com/tiqi-group/pydase_service_base.git#main[ionizer]"
  ```
- For `InfluxDBv1Session`, include the `influxdbv1` extra:
  ```bash
  poetry add "git+https://github.com/tiqi-group/pydase_service_base.git#main[influxdbv1]"
  ```
- For `InfluxDBSession`, include the `influxdbv2` extra:
  ```bash
  poetry add "git+https://github.com/tiqi-group/pydase_service_base.git#main[influxdbv2]"
  ```
- For `PostgresDatabaseSession`, include the `postgresql` extra:
  ```bash
  poetry add "git+https://github.com/tiqi-group/pydase_service_base.git#main[postgresql]"
  ```

or directly add the following line to the `pyproject.toml` file:

```toml
pydase_service_base = {git = "https://github.com/tiqi-group/pydase_service_base.git", rev = "main", extras = ["ionizer", "postgresql", "influxdbv1", "influxdbv2"]}
```

## Configuration

Database connections rely on configurations provided by environment variables or a specific configuration file. The package anticipates a `database_config` folder in the root directory of any module using this package. This folder should house the database configuration files. You can override the `database_config` folder's location by passing a different path to the database classes' constructor.

Structure of the `database_config` folder:

```
database_config
├── influxdbv1_config.yaml
├── influxdb_config.yaml
├── postgres_development.yaml
└── postgres_production.yaml
```

Example content for the configuration files:

`influxdbv1_config.yaml`:
```yaml
host: https://influxdb.phys.ethz.ch
port: 443  # defaults to 8086 (default port of influxdb)
username: root
password: root
database: my_database
ssl: True  # defaults to True
verify_ssl: True  # defaults to True
headers:
  Host: other-virtual-host.ethz.ch
```

`influxdb_config.yaml`:
```yaml
url: https://database-url.ch
org: your-org
token: <influxdb-token>
verify_ssl: True  # defaults to True
headers:
  Host: other-virtual-host.ethz.ch
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

### InfluxDBv1Session

Interact with an InfluxDBv1 server using the `InfluxDBv1Session` class. **Note that this class only supports InfluxDB v1** and **requires the `influxdbv1` optional dependency**.

```python
from pydase_service_base.database import InfluxDBv1Session

with InfluxDBv1Session() as influx_client:
    # Writing points to a database
    points = [
        {
            "measurement": "your_measurement",  # Replace with your measurement
            "tags": {
                "example_tag": "tag_value",  # Replace with your tag and value
            },
            "fields": {
                "example_field": 123,  # Replace with your field and its value
            },
            "time": "2023-06-05T00:00:00Z",  # Replace with your timestamp
        }
    ]
    influx_client.write_points(points=points, database="other_database")
```

**Note** that you have to set `ssl` and `verify_ssl` to `False` when you are using a local influxdb instance.


### InfluxDBv3Session

Interact with an InfluxDB 3.x server using the `InfluxDBv3Session` class. **This requires the `influxdbv3` optional dependency**.

#### Example configuration file (`database_config/influxdbv3_config.yaml`):

```yaml
url: http://localhost:8181
org: test-org
bucket: test-bucket
token: <your-admin-token>
verify_ssl: false
```

#### Example usage:

```python
from pydase_service_base.database.influxdbv3_session import InfluxDBv3Session, WritePrecision
from influxdb_client_3 import Point
import time

# Option 1: Initialize from config file (recommended)
with InfluxDBv3Session.from_config_file() as session:
    point = Point("temperature").tag("location", "office").field("value", 23.5).time(int(time.time() * 1e9), WritePrecision.NS)
    session.write(bucket="test-bucket", record=point)
    # Query data (returns a pyarrow.Table)
    table = session._client.query('SELECT * FROM "test-bucket" WHERE location = \'office\'', language="sql")
    print(table.to_pandas())

# Option 2: Initialize directly
with InfluxDBv3Session(
    host="http://localhost:8181",
    org="test-org",
    bucket="test-bucket",
    token="<your-admin-token>",
    verify_ssl=False,
) as session:
    # ... same as above ...
    pass
```

**Note:**
- You must create the bucket (`test-bucket`) before writing data.
- The token must have sufficient privileges to write and query data.

---

### InfluxDBSession

Interact with an InfluxDB server using the `InfluxDBSession` class. **Note that this class only supports InfluxDB v2** and **requires the `influxdbv2` optional dependency**.

```python
from pydase_service_base.database import InfluxDBSession

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
    influx_client.write(
        bucket='my_new_bucket', record=record
    )
```

### PostgresDatabaseSession

The `PostgresDatabaseSession` class allows interactions with a PostgreSQL database. **This class requires the `postgresql` optional dependency**.

```python
from pydase_service_base.database import PostgresDatabaseSession
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

### Ionizer Interface

The `IonizerServer` provides an interface to integrate `pydase` applications with Ionizer seamlessly. **This requires the `ionizer` optional dependency**.

To deploy `IonizerServer` with your service:

```python
from pydase_service_base.ionizer_interface import IonizerServer

class YourServiceClass:
    # your implementation...


if __name__ == "__main__":
    # Instantiate your service
    service = YourServiceClass()

    # Start the main pydase server with IonizerServer as an additional server
    Server(
        service,
        additional_servers=[
            {
                "server": IonizerServer,
                "port": 8002,
                "kwargs": {},
            }
        ],
    ).run()
```

This integration ensures that your primary `pydase` server and `YourServiceClass` service are set up. It also incorporates the `IonizerServer` on port `8002`.

For more details on the `IonizerServer`, get in touch with the maintainers.

## License

This project uses the MIT License. Consult the [LICENSE](./LICENSE) file for more information.
