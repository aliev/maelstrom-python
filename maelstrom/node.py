import asyncio
import datetime
import json
import logging
import time
from typing import Any, Callable, Coroutine, TypeAlias

from maelstrom.protocol import Body, Message

Handler: TypeAlias = Callable[["Node", Message], Coroutine[Any, Any, Any]]

logger = logging.getLogger(__name__)


class Node:
    def __init__(self):
        self.node_ids: set[str] = set()
        self.handlers: dict[str, Handler] = {}
        self.callbacks: dict[int, Handler] = {}
        self.node_id: str = ""
        self.next_msg_id = 0

        self._lock = asyncio.Lock()
        self._log_lock = asyncio.Lock()

    def set_io(
        self,
        request: asyncio.StreamReader,
        response: asyncio.StreamWriter,
        stderr: asyncio.StreamWriter,
    ):
        self.request = request
        self.response = response
        self.stderr = stderr

    def on(self, name: str | None = None):
        """Registers new handler for node."""

        def inner(handler: Handler):
            handler_name = handler.__name__ if name is None else name

            if handler_name in self.handlers:
                logger.error("Already registered handler for %s", handler_name)

            self.handlers[handler_name] = handler

        return inner

    async def rpc(
        self,
        dest: str,
        body: Body,
        handler: Handler,
    ):
        """
        Send an async RPC request.
        Invokes handler with response message once one arrives.
        """
        self.next_msg_id += 1
        msg_id = self.next_msg_id

        self.callbacks[msg_id] = handler

        await self.send(dest, {**body, "msg_id": msg_id})

    async def reply(self, req: Message, body: Body):
        """Reply with body to incoming message

        Args:
            req (Message): incoming message
            body (Body): body.
        """
        self.next_msg_id += 1

        msg_id = req.get("body", {}).get("msg_id", None)

        if msg_id is None:
            await self.log("Cannot parse 'req': 'msg_is' is not presented.")
            return

        body = {**body, "in_reply_to": msg_id, "msg_id": self.next_msg_id}

        await self.send(req["src"], body)

    async def log(self, msg: str, *args) -> None:
        """Thread safe and async version of log.

        Args:
            msg (str): log message.
        """
        # async with self._log_lock:
        date_time = datetime.datetime.fromtimestamp(time.time()).strftime("%H:%M:%S.%f")
        log_message = f"{date_time}: {msg}\n" % args
        self.stderr.write(log_message.encode())
        await self.stderr.drain()

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

        # async with self._lock:
        self.response.write((result + "\n").encode())
        await self.response.drain()
        await self.log("Respond with message '%s'", result)
