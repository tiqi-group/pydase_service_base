import logging
from enum import Enum
from typing import Any

import pydase
import pydase.components
import pydase.units as u
import pydase.version
import tiqi_rpc
from pydase.data_service.data_service_observer import DataServiceObserver
from pydase.utils.helpers import get_object_attr_from_path  # type: ignore
from pydase.utils.serialization.types import SerializedObject

from pydase_service_base.ionizer_interface.rpc_interface import RPCInterface

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
            RPCInterface(self.data_service_observer, **kwargs),
            host=host,
            port=port,  # type: ignore
        )

        self.data_service_observer.add_notification_callback(self.notify_ionizer)
        self.server.install_signal_handlers = lambda: None  # type: ignore

    def notify_ionizer(
        self, full_access_path: str, value: Any, cached_value: SerializedObject
    ) -> None:
        """This function notifies Ionizer about changed values.

        Args:
        full_access_path (str):
            The full access path of the parameter.
        value (Any):
            The new value of the parameter.
        cached_value (SerializedObject):
            The serialized representation of the cached parameter.
        """
        attr_name = full_access_path.split(".")[-1]
        if isinstance(value, Enum):
            value = value.value
        if isinstance(value, u.Quantity):
            value = value.m
        if attr_name == "value":
            parent_path = ".".join(full_access_path.split(".")[:-1])
            parent_object = get_object_attr_from_path(self.service, parent_path)
            if isinstance(parent_object, pydase.components.NumberSlider):
                # removes the "value" from name -> Ionizer does not know about the
                # internals of NumberSlider
                full_access_path = parent_path

        logger.debug(
            "Updating Ionizer with %s", {"name": full_access_path, "value": value}
        )
        return self.server._handler.notify(  # type: ignore
            {"name": full_access_path, "value": value}
        )

    async def serve(self) -> None:
        await self.server.serve()
