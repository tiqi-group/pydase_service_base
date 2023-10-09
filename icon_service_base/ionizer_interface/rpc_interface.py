import inspect
from enum import Enum
from typing import Any, Optional

from pydase import DataService
from pydase.components import NumberSlider
from pydase.units import Quantity
from pydase.utils.helpers import get_object_attr_from_path
from pydase.version import __version__


class RPCInterface(object):
    """RPC interface to be passed to tiqi_rpc.Server to interface with Ionizer."""

    def __init__(
        self, service: DataService, info: dict[str, Any] = {}, *args: Any, **kwargs: Any
    ) -> None:
        self._service = service
        self._info = info

    async def version(self) -> str:
        return f"pydase v{__version__}"

    async def name(self) -> str:
        return self._service.__class__.__name__

    async def info(self) -> dict:
        return self._info

    async def get_props(self, name: Optional[str] = None) -> dict[str, Any]:
        if name is None:
            return self._service.serialize()
        return self._service.serialize()

    async def get_param(self, full_access_path: str) -> Any:
        """Returns the value of the parameter given by the full_access_path.

        This method is called when Ionizer initilizes the Plugin or refreshes. The
        widgets need to store the full_access_path in their name attribute.
        """
        param = get_object_attr_from_path(self._service, full_access_path.split("."))
        if isinstance(param, NumberSlider):
            return param.value
        elif isinstance(param, DataService):
            return param.serialize()
        elif inspect.ismethod(param):
            # explicitly serialize any methods that will be returned
            full_access_path = param.__name__
            args = inspect.signature(param).parameters
            return f"{full_access_path}({', '.join(args)})"
        elif isinstance(param, Enum):
            return param.value
        elif isinstance(param, Quantity):
            return param.m
        else:
            return param

    async def set_param(self, full_access_path: str, value: Any) -> None:
        parent_path_list = full_access_path.split(".")[:-1]
        parent_object = get_object_attr_from_path(self._service, parent_path_list)
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
            elif isinstance(current_value, NumberSlider):
                parent_path_list.append(attr_name)
                attr_name = "value"
        self._service.update_DataService_attribute(parent_path_list, attr_name, value)

    async def remote_call(self, full_access_path: str, *args: Any) -> Any:
        full_access_path_list = full_access_path.split(".")
        method_object = get_object_attr_from_path(self._service, full_access_path_list)
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
