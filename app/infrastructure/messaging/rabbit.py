from __future__ import annotations

import json
import logging
from typing import Any

import pika
from pika import spec

from oficina_contracts.routing import EXCHANGE_EVENTS

log = logging.getLogger(__name__)


class RabbitPublisher:
    def __init__(self, amqp_url: str) -> None:
        self._url = amqp_url
        self._connection: pika.BlockingConnection | None = None
        self._channel: spec.Channel | None = None

    def connect(self) -> None:
        if self._connection and self._connection.is_open:
            return
        params = pika.URLParameters(self._url)
        self._connection = pika.BlockingConnection(params)
        self._channel = self._connection.channel()
        self._channel.exchange_declare(
            exchange=EXCHANGE_EVENTS, exchange_type="topic", durable=True
        )

    def close(self) -> None:
        if self._connection and self._connection.is_open:
            self._connection.close()
        self._connection = None
        self._channel = None

    def publish(self, routing_key: str, body: dict[str, Any]) -> None:
        self.connect()
        assert self._channel is not None
        self._channel.basic_publish(
            exchange=EXCHANGE_EVENTS,
            routing_key=routing_key,
            body=json.dumps(body, default=str),
            properties=pika.BasicProperties(delivery_mode=2, content_type="application/json"),
        )


def publish_event(amqp_url: str | None, routing_key: str, body: dict[str, Any]) -> bool:
    if not amqp_url:
        log.debug("rabbitmq desabilitado; evento %s não publicado", routing_key)
        return False
    pub = RabbitPublisher(amqp_url)
    try:
        pub.publish(routing_key, body)
        return True
    finally:
        pub.close()
