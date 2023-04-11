from __future__ import annotations

import loguru
from kombu import Connection, Exchange, Producer
from settings import amqp_settings

from .LogBroadcastMessage import LogBroadcastMessage, LogBroadcastMessageLevel


class LogBroadcastMessagePublisher:
    def __init__(self, originator: str) -> None:
        self._originator = originator
        self._exchange = Exchange("logging", type="topic", durable=True)

        self._connection = Connection(amqp_settings.broker_dsn)
        self._channel = self._connection.channel()
        bound_exchange = self._exchange(self._channel)
        bound_exchange.declare()
        self._producer = Producer(channel=self._channel, exchange=self._exchange)

    def send_msg(self, loguru_msg: loguru.Message):
        loguru_dict = loguru_msg.record
        package = loguru_dict["name"] if loguru_dict["name"] is not None else ""

        icon_msg = LogBroadcastMessage(
            originator=self._originator,
            level=LogBroadcastMessageLevel(loguru_dict["level"].name),
            message=loguru_dict["message"],
            package=package,
            line_number=str(loguru_dict["line"]),
            function=loguru_dict["function"],
            timestamp=loguru_dict["time"],
        )

        self._producer.publish(
            icon_msg.json(),
            exchange=self._exchange,
            expiration=amqp_settings.message_expiration_default_s,
            routing_key=icon_msg.routing_key,
        )
