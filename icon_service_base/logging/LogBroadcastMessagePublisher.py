from __future__ import annotations

from kombu import Connection, Exchange, Producer  # type: ignore
from loguru import Record, Message

from settings import amqp_settings

from .LogBroadcastMessage import LogBroadcastMessage


class LogBroadcastMessagePublisher:
    def __init__(self, originator: str) -> None:
        self._originator = originator
        self._exchange = Exchange("logging", type="topic", durable=True)

        self._connection = Connection(amqp_settings.broker_dsn)
        self._channel = self._connection.channel()
        bound_exchange = self._exchange(self._channel)
        bound_exchange.declare()
        self._producer = Producer(channel=self._channel, exchange=self._exchange)

    def send_msg(self, loguru_msg: Message):
        loguru_dict: Record = loguru_msg.record

        icon_msg = LogBroadcastMessage(
            originator=self._originator,
            level=loguru_dict["level"].name,
            message=loguru_dict["message"],
            package=loguru_dict["name"],
            line_number=loguru_dict["line"],
            function=loguru_dict["function"],
            timestamp=loguru_dict["time"],
        )

        self._producer.publish(  # type: ignore
            icon_msg.json(),
            exchange=self._exchange,
            expiration=amqp_settings.message_expiration_default_s,
            routing_key=icon_msg.routing_key,
        )
