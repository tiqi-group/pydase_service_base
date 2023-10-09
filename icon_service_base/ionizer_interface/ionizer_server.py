from enum import Enum
from typing import Any

import pydase
import pydase.components
import pydase.units as u
import tiqi_rpc
from pydase.utils.helpers import get_object_attr_from_path

from icon_service_base.ionizer_interface.rpc_interface import RPCInterface


class IonizerServer:
    def __init__(
        self, service: pydase.DataService, port: int, host: str, **kwargs: Any
    ) -> None:
        self.server = tiqi_rpc.Server(
            RPCInterface(service, **kwargs), host=host, port=port  # type: ignore
        )

        def notify_Ionizer(parent_path: str, attr_name: str, value: Any) -> None:
            """This function notifies Ionizer about changed values.

            Args:
            - parent_path (str): The parent path of the parameter.
            - attr_name (str): The name of the changed parameter.
            - value (Any): The value of the parameter.
            """
            parent_path_list = parent_path.split(".")[1:]  # without classname
            name = ".".join(parent_path_list + [attr_name])
            if isinstance(value, Enum):
                value = value.value
            if isinstance(value, u.Quantity):
                value = value.m
            if attr_name == "value":
                parent_object = get_object_attr_from_path(service, parent_path_list)
                if isinstance(parent_object, pydase.components.NumberSlider):
                    # removes the "value" from name -> Ionizer does not know about the
                    # internals of NumberSlider
                    name = ".".join(name.split(".")[:-1])

            return self.server._handler.notify(  # type: ignore
                {"name": name, "value": value}
            )

        service._callback_manager.add_notification_callback(notify_Ionizer)
        self.server.install_signal_handlers = lambda: None

    async def serve(self) -> None:
        await self.server.serve()
