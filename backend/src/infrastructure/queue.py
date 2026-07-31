"""Azure Service Bus client wrapper (T012).

Implements the inbound event queue/replay path (FR-022): events are enqueued here and
consumed by `src/domain/inventory/replay_worker.py`. An in-memory implementation is
provided for local development and tests so contributors do not need a live Service Bus
namespace to exercise the ingestion flow end-to-end.
"""

from __future__ import annotations

import json
from collections import deque
from typing import Protocol

from src.infrastructure.config import get_settings


class EventQueueClient(Protocol):
    def send_event(self, payload: dict) -> None: ...

    def receive_events(self, max_messages: int = 32) -> list[dict]:
        """Receive and remove up to `max_messages` queued events (at-least-once delivery)."""
        ...

    def dead_letter(self, payload: dict) -> None: ...

    def replay_dead_lettered(self, max_messages: int = 32) -> list[dict]: ...


class InMemoryQueueClient:
    """Local/dev/test substitute for Azure Service Bus. Not for production use."""

    def __init__(self) -> None:
        self._queue: deque[dict] = deque()
        self._dead_letter: deque[dict] = deque()

    def send_event(self, payload: dict) -> None:
        self._queue.append(payload)

    def receive_events(self, max_messages: int = 32) -> list[dict]:
        received = []
        while self._queue and len(received) < max_messages:
            received.append(self._queue.popleft())
        return received

    def dead_letter(self, payload: dict) -> None:
        self._dead_letter.append(payload)

    def replay_dead_lettered(self, max_messages: int = 32) -> list[dict]:
        replayed = []
        while self._dead_letter and len(replayed) < max_messages:
            replayed.append(self._dead_letter.popleft())
        return replayed


class ServiceBusQueueClient:
    """Production client backed by azure-servicebus. Requires `service_bus_connection_string`."""

    def __init__(self) -> None:
        from azure.servicebus import (
            ServiceBusClient,  # local import: optional dependency at runtime
        )

        settings = get_settings()
        if not settings.service_bus_connection_string:
            raise RuntimeError("APP_SERVICE_BUS_CONNECTION_STRING is required for ServiceBusQueueClient")
        self._settings = settings
        self._client = ServiceBusClient.from_connection_string(settings.service_bus_connection_string)

    def send_event(self, payload: dict) -> None:
        from azure.servicebus import ServiceBusMessage

        with self._client.get_queue_sender(self._settings.service_bus_queue_name) as sender:
            sender.send_messages(ServiceBusMessage(json.dumps(payload)))

    def receive_events(self, max_messages: int = 32) -> list[dict]:
        with self._client.get_queue_receiver(self._settings.service_bus_queue_name) as receiver:
            messages = receiver.receive_messages(max_message_count=max_messages, max_wait_time=5)
            events = []
            for message in messages:
                events.append(json.loads(str(message)))
                receiver.complete_message(message)
            return events

    def dead_letter(self, payload: dict) -> None:
        # Production implementation would use the receiver's dead_letter_message on the
        # original message; simplified here to re-publish onto a dead-letter-tagged payload.
        self.send_event({**payload, "_dead_lettered": True})

    def replay_dead_lettered(self, max_messages: int = 32) -> list[dict]:
        events = self.receive_events(max_messages=max_messages)
        return [e for e in events if e.get("_dead_lettered")]


_queue_client: EventQueueClient | None = None


def get_queue_client() -> EventQueueClient:
    global _queue_client
    if _queue_client is None:
        settings = get_settings()
        _queue_client = (
            ServiceBusQueueClient() if settings.service_bus_connection_string else InMemoryQueueClient()
        )
    return _queue_client


def set_queue_client_for_testing(client: EventQueueClient) -> None:
    global _queue_client
    _queue_client = client
