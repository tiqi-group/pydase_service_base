from abc import abstractmethod
from uuid import uuid4

from kombu import Connection, Consumer, Exchange, Message, Queue
from loguru import logger

from settings import amqp_settings


class LogBroadcastMessageListener:
    def __init__(self):
        queue_name = f"logging-listener-{uuid4()}"

        self._exchange = Exchange("logging", type="topic", durable=True)
        self._connection = Connection(amqp_settings.broker_dsn)
        self._channel = self._connection.channel()

        self._queue = Queue(
            queue_name,
            self._exchange,
            routing_key="#",
            durable=False,
            auto_delete=True,
            exclusive=True,
        )
        self._consumer = Consumer(self._channel, [self._queue])
        self._consumer.register_callback(self.message_callback)  # type: ignore
        with self._consumer:  # type: ignore
            while True:
                self._connection.drain_events()  # type: ignore

    @abstractmethod
    def message_callback(self, body: str, message: Message) -> None:
        ...
