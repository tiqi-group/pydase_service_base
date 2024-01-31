import logging
from enum import Enum
from typing import Any

import pydase
import pydase.components
import pydase.units as u
import tiqi_rpc
from pydase.data_service.data_service_observer import DataServiceObserver
from pydase.utils.helpers import get_object_attr_from_path_list

from icon_service_base.ionizer_interface.rpc_interface import RPCInterface

logger = logging.getLogger(__name__)


class IonizerServer:
    def __init__(
        self,
        data_service_observer: DataServiceObserver,
        host: str,
        port: int,
        **kwargs: Any,
    ) -> None:
        self.data_service_observer = data_service_observer
        self.service = self.data_service_observer.state_manager.service
        self.server = tiqi_rpc.Server(
            RPCInterface(self.service, **kwargs),
            host=host,
            port=port,  # type: ignore
        )

        self.data_service_observer.add_notification_callback(self.notify_Ionizer)
        self.server.install_signal_handlers = lambda: None  # type: ignore

    def notify_Ionizer(
        self, full_access_path: str, value: Any, cached_value: dict[str, Any]
    ) -> None:
        """This function notifies Ionizer about changed values.

        Args:
        - parent_path (str): The parent path of the parameter.
        - attr_name (str): The name of the changed parameter.
        - value (Any): The value of the parameter.
        """
        parent_path_list, attr_name = (
            full_access_path.split(".")[:-1],
            full_access_path.split(".")[-1],
        )  # without classname
        if isinstance(value, Enum):
            value = value.value
        if isinstance(value, u.Quantity):
            value = value.m
        if attr_name == "value":
            parent_object = get_object_attr_from_path_list(
                self.service, parent_path_list
            )
            if isinstance(parent_object, pydase.components.NumberSlider):
                # removes the "value" from name -> Ionizer does not know about the
                # internals of NumberSlider
                full_access_path = ".".join(full_access_path.split(".")[:-1])

        return self.server._handler.notify(  # type: ignore
            {"name": full_access_path, "value": value}
        )

    async def serve(self) -> None:
        await self.server.serve()
