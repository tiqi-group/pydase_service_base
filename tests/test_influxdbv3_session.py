import re
import time

import pytest
from influxdb_client_3 import Point
from testcontainers.core.container import DockerContainer

from pydase_service_base.database.influxdbv3_session import InfluxDBv3Session

INFLUXDB_IMAGE = "influxdb:3.3-core"
INFLUXDB_PORT = 8181
INFLUXDB_ORG = "test-org"
INFLUXDB_BUCKET = "test-bucket"
INFLUXDB_TOKEN = "test-token"
INFLUXDB_DATABASE = "test-database"


def parse_influxdb3_token(output: str) -> str:
    """
    Extract the token from the output of 'influxdb3 create token --admin',
    handling ANSI escape codes.
    Raises ValueError if not found.
    """
    ansi_escape = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
    clean_output = ansi_escape.sub("", output)

    for line in clean_output.splitlines():
        line_strip = line.strip()
        if line_strip.startswith("Token:"):
            return line_strip.split("Token:", 1)[1].strip()
    raise ValueError("Token not found in output")


@pytest.fixture
def influxdbv3_config_yaml(tmp_path, monkeypatch):
    """
    Create a temporary influxdbv3_config.yaml and patch ServiceConfig to point to it.
    """
    config_dir = tmp_path / "database_config"
    config_dir.mkdir()
    config_file = config_dir / "influxdbv3_config.yaml"
    config_file.write_text(
        """
url: http://localhost:9999
org: test-org
bucket: test-bucket
token: test-token
verify_ssl: false
"""
    )
    monkeypatch.chdir(tmp_path)
    return config_file


@pytest.fixture(scope="session")
def influxdb_container():
    """Spin up an InfluxDB 3.x container for integration testing."""
    with (
        DockerContainer(INFLUXDB_IMAGE)
        .with_exposed_ports(INFLUXDB_PORT)
        .with_bind_ports(INFLUXDB_PORT, 8181)
        .with_command(
            "influxdb3 serve "
            "--node-id host01 "
            "--object-store memory "
            "--data-dir ~/.influxdb3"
        )
    ) as container:
        raw_token = (
            container.exec(["influxdb3", "create", "token", "--admin"])
            .output.decode()
            .strip()
        )
        admin_token = parse_influxdb3_token(raw_token)
        host = container.get_container_host_ip()
        port = INFLUXDB_PORT
        url = f"http://{host}:{port}"

        headers = {"Authorization": f"Bearer {admin_token}"}

        for _ in range(10):
            try:
                import requests

                print(f"Checking InfluxDB health at {url}/health")
                resp = requests.get(f"{url}/health", headers=headers, timeout=2)
                if resp.status_code == 200:
                    break
            except Exception:
                pass
            time.sleep(1)
        else:
            raise RuntimeError("InfluxDB did not become healthy in time")
        create_bucket_cmd = [
            "influxdb3",
            "create",
            "database",
            "--token",
            admin_token,
            INFLUXDB_BUCKET,
        ]
        container.exec(create_bucket_cmd)
        yield {
            "url": url,
            "org": INFLUXDB_ORG,
            "bucket": INFLUXDB_BUCKET,
            "token": admin_token,
        }


@pytest.mark.skip(reason="Requires Docker run in background, enable when needed")
def test_influxdbv3session_write(influxdb_container):
    """Test writing and querying a point using InfluxDBv3Session."""
    url = influxdb_container["url"]
    org = influxdb_container["org"]
    bucket = influxdb_container["bucket"]
    token = influxdb_container["token"]

    with InfluxDBv3Session(
        host=url,
        org=org,
        bucket=bucket,
        token=token,
        verify_ssl=False,
    ) as session:
        point = Point("temperature").tag("location", "office").field("value", 23.5)
        session.write(bucket=bucket, record=point)

        time.sleep(1)

        result = session._client.query(
            "SELECT * FROM temperature",
            database=bucket,
        )
        assert result is not None
        assert result["value"][0].as_py() == 23.5  # type: ignore




def test_from_config_file_initialization(influxdbv3_config_yaml):
    """
    Test that InfluxDBv3Session.from_config_file initializes correctly from config file.
    """
    session = InfluxDBv3Session.from_config_file()
    assert session._client is not None
    # Check that the client has the expected attributes
    assert session._host == "http://localhost:9999"
    assert session._org == "test-org"
    assert session._bucket == "test-bucket"
    assert session._token == "test-token"
