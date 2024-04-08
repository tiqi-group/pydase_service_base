import copy
import inspect
import re
from enum import Enum
from typing import Any

from pydase import DataService
from pydase.components import NumberSlider
from pydase.data_service.data_service_observer import DataServiceObserver
from pydase.units import Quantity
from pydase.utils.helpers import get_object_attr_from_path
from pydase.utils.serialization.serializer import (
    dump,
    generate_serialized_data_paths,
    get_nested_dict_by_path,
)
from pydase.utils.serialization.types import SerializedMethod, SerializedObject
from pydase.version import __version__


def extract_type_name(type_annotation: str) -> str | None:
    """Extracts the type name from annotation string. For builtin types, the type string
    is enclosed like this: "<class 'type_str'>".

    Example:
        >>> type_annotation = "<class 'int'>"
        >>> print(extract_type_name(type_annotation))
        int
    """
    match = re.search(r"'([^']*)'", type_annotation)
    if match:
        return match.group(1)
    return None


def add_parameters_keyword_to_dict(
    serialized_method: SerializedMethod,
) -> None:
    """Adds "parameters" key-value pair to serialized_method dictionary."""
    parameters: dict[str, str | None] = {}
    for name, param_signature in serialized_method["signature"]["parameters"].items():
        parameters[name] = extract_type_name(param_signature["annotation"])

    # adds the parameters keyword to the dictionary as Ionizer is expecting this
    serialized_method["parameters"] = parameters  # type: ignore


def update_method_serialization(
    serialized_object: dict[str, Any],
) -> dict[str, Any]:
    """Adds a "parameter" key-value pair to each serialized method within
    serialized_object."""
    for path in generate_serialized_data_paths(serialized_object):
        nested_dict = get_nested_dict_by_path(serialized_object, path)
        if nested_dict["type"] == "method":
            add_parameters_keyword_to_dict(nested_dict)

    return serialized_object


class RPCInterface:
    """RPC interface to be passed to tiqi_rpc.Server to interface with Ionizer."""

    def __init__(
        self, data_service_observer: DataServiceObserver, *args: Any, **kwargs: Any
    ) -> None:
        self._data_service_observer = data_service_observer
        self._state_manager = self._data_service_observer.state_manager
        self._service = self._state_manager.service

    async def version(self) -> str:
        return f"pydase v{__version__}"

    async def name(self) -> str:
        return self._service.__class__.__name__

    async def get_props(self) -> SerializedObject:
        return update_method_serialization(
            copy.deepcopy(self._service.serialize()["value"])  # type: ignore
        )

    async def get_param(self, full_access_path: str) -> Any:
        """Returns the value of the parameter given by the full_access_path.

        This method is called when Ionizer initilizes the Plugin or refreshes. The
        widgets need to store the full_access_path in their name attribute.
        """
        param = get_object_attr_from_path(self._service, full_access_path)
        if isinstance(param, NumberSlider):
            return param.value
        if isinstance(param, DataService):
            return param.serialize()
        if inspect.ismethod(param):
            # explicitly serialize any methods that will be returned
            full_access_path = param.__name__
            args = inspect.signature(param).parameters
            return f"{full_access_path}({', '.join(args)})"
        if isinstance(param, Enum):
            return param.value
        if isinstance(param, Quantity):
            return param.m
        return param

    async def set_param(self, full_access_path: str, value: Any) -> None:
        parent_path = ".".join(full_access_path.split(".")[:-1])
        parent_object = get_object_attr_from_path(self._service, parent_path)
        attr_name = full_access_path.split(".")[-1]
        # I don't want to trigger the execution of a property getter as this might take
        # a while when connecting to remote devices
        if not isinstance(
            getattr(type(parent_object), attr_name, None),
            property,
        ):
            current_value = getattr(parent_object, attr_name, None)
            if isinstance(current_value, Enum) and isinstance(value, int):
                # Ionizer sets the enums using the position of the definition order
                # This works as definition order is kept, see e.g.
                # https://docs.python.org/3/library/enum.html#enum.EnumType.__iter__
                # I need to use the name attribute as this is what
                # DataService.__set_attribute_based_on_type expects
                value = list(current_value.__class__)[value].name
            if isinstance(current_value, Quantity):
                value = value * current_value.u
            elif isinstance(current_value, NumberSlider):
                full_access_path = full_access_path + "value"

        self._state_manager.set_service_attribute_value_by_path(
            full_access_path, dump(value)
        )

    async def remote_call(self, full_access_path: str, *args: Any) -> Any:
        method_object = get_object_attr_from_path(self._service, full_access_path)
        return method_object(*args)

    async def emit(self, message: str) -> None:
        self.notify(message)

    def notify(self, message: str) -> None:
        """
        This method will be overwritten by the tiqi-rpc server.

        Args:
            message (str): Notification message.
        """
        return
