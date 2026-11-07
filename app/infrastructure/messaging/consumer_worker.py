from __future__ import annotations

import json
import logging
import threading
import time

import pika

from app.application.saga.os_handlers import handle_incoming_event
from app.infrastructure.config import get_settings
from app.infrastructure.database.connection import SessionLocal
from app.infrastructure.messaging.outbox import flush_outbox
from app.infrastructure.mongo.timeline import OsEventTimeline
from oficina_contracts.routing import EXCHANGE_EVENTS

log = logging.getLogger(__name__)


def _consume_loop(stop: threading.Event) -> None:
    url = get_settings().rabbitmq_url
    if not url:
        return
    timeline = OsEventTimeline(get_settings().mongodb_url or None)
    while not stop.is_set():
        try:
            conn = pika.BlockingConnection(pika.URLParameters(url))
            ch = conn.channel()
            ch.exchange_declare(exchange=EXCHANGE_EVENTS, exchange_type="topic", durable=True)
            q = ch.queue_declare(queue="os-service.saga", durable=True)
            for key in (
                "budget.#",
                "payment.#",
                "execution.#",
                "compensate.#",
            ):
                ch.queue_bind(exchange=EXCHANGE_EVENTS, queue=q.method.queue, routing_key=key)

            def _on(ch_, method, _props, body: bytes) -> None:
                db = SessionLocal()
                try:
                    handle_incoming_event(db, timeline, body)
                    ch_.basic_ack(delivery_tag=method.delivery_tag)
                except Exception:  # noqa: BLE001
                    log.exception("erro ao processar evento saga")
                    ch_.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                    db.rollback()
                finally:
                    db.close()

            ch.basic_qos(prefetch_count=10)
            ch.basic_consume(queue=q.method.queue, on_message_callback=_on)
            while not stop.is_set():
                conn.process_data_events(time_limit=1)
            conn.close()
        except Exception:  # noqa: BLE001
            log.warning("consumidor rabbitmq; retry em 3s")
            time.sleep(3)


def _outbox_loop(stop: threading.Event) -> None:
    while not stop.is_set():
        db = SessionLocal()
        try:
            flush_outbox(db, get_settings().rabbitmq_url or None)
        finally:
            db.close()
        time.sleep(2)


def start_background_workers(stop: threading.Event) -> list[threading.Thread]:
    threads = [
        threading.Thread(target=_consume_loop, args=(stop,), daemon=True, name="rmq-consumer"),
        threading.Thread(target=_outbox_loop, args=(stop,), daemon=True, name="outbox-flush"),
    ]
    for t in threads:
        t.start()
    return threads
