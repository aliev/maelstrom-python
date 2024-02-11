import asyncio
import logging
import json
from typing import Any, Callable, Coroutine
from maelstrom.protocol import Body, Message

type Handler = Callable[[Node, Message], Coroutine[Any, Any, Any]]


class Node:
    def __init__(self):
        self.node_ids: set[str] = set()
        self.handlers: dict[str, Handler] = {}
        self.node_id: str = ""

    def set_io(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        logger: asyncio.StreamWriter
    ):
        self.reader = reader
        self.writer = writer
        self.logger = logger

    def on(self, msg_type: str):
        def inner(handler: Handler):
            if msg_type in self.handlers:
                logging.error("Already registered handler for %s", msg_type)

            self.handlers[msg_type] = handler

        return inner

    async def set_node_id(self, node_id: str):
        self.node_id = node_id

    async def set_node_ids(self, node_ids: set[str]):
        self.node_ids.update(node_ids)

    async def reply(self, src: str, body: Body):
        await self.send(src, body)

    async def log(self, msg: str) -> None:
        self.logger.write((msg + "\n").encode())
        await self.writer.drain()

    async def send(self, dest: str, body: Body):
        message: Message = {
            "src": self.node_id,
            "dest": dest,
            "body": body,
        }

        try:
            result = json.dumps(message)
        except TypeError:
            logging.exception("Cannot decode object")
            return None

        self.writer.write(result.encode())
        await self.writer.drain()

        await self.log(f"Respond with message {result}")
