
import pytest
from confz import BaseConfig, FileSource

from pydase_service_base.database.create_config import (
    NoConfigSourceError,
    create_config,
)


class DummyConfig(BaseConfig):
    foo: str
    CONFIG_SOURCES = None


def test_create_config_with_config_folder_and_file(tmp_path):
    config_folder = tmp_path / "my_config"
    config_folder.mkdir()
    config_file = config_folder / "dummy.yaml"
    config_file.write_text("foo: bar\n")

    # Should load config from the specified folder and file
    config = create_config(
        DummyConfig, config_folder=config_folder, config_file="dummy.yaml"
    )
    assert config.foo == "bar"


def test_create_config_with_config_class_sources(tmp_path):
    # DummyConfigWithSource has CONFIG_SOURCES set
    class DummyConfigWithSource(BaseConfig):
        foo: str
        CONFIG_SOURCES = FileSource(tmp_path / "dummy.yaml")

    config_file = tmp_path / "dummy.yaml"
    config_file.write_text("foo: qux\n")

    config = create_config(DummyConfigWithSource, config_file="dummy.yaml")
    assert config.foo == "qux"


def test_create_config_raises_when_no_config_source(tmp_path):
    # DummyConfigNoSource has CONFIG_SOURCES = None and no config_folder provided
    class DummyConfigNoSource(BaseConfig):
        foo: str
        CONFIG_SOURCES = None

    with pytest.raises(NoConfigSourceError) as excinfo:
        create_config(DummyConfigNoSource, config_file="dummy.yaml")
    assert "No 'database_config' folder found" in str(excinfo.value)
