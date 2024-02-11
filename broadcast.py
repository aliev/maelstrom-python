#!/usr/bin/env python

import json
import sys
from typing import IO, Callable
from multiprocessing import Lock, RLock
from maelstrom.protocol import Body, Message


Handler = Callable[["Node", Message], None]



class Node:
    def __init__(
        self,
        logger: IO[str] = sys.stderr,
        node_id: int | None = None,
        node_ids: list[int] | None = None,
    ):
        self.node_id = node_id
        self.node_ids = node_ids
        self.next_msg_id = 0
        self.neighbors = []

        self.handlers: dict[str, Handler] = {}

        self.logger = logger

        self.lock = RLock()
        self.log_lock = Lock()

    def log(self, message: str):
        with self.log_lock:
            self.logger.write(message)
            self.logger.write("\n")
            self.logger.flush()

    def send(self, dest, body):
        msg = {
            "dest": dest,
            "src": self.node_id,
            "body": body
        }

        with self.lock:
            self.log(f"Sent {msg}")
            json.dump(msg, sys.stdout)
            sys.stdout.write("\n")
            sys.stdout.flush()

    def parse_msg(self, line) -> Message:
        return json.loads(line)

    def reply(self, msg: Message, body: Body):
        body = msg["body"]

        if "msg_in" not in body:
            raise ValueError(f"Key msg_in expected in body.")

        self.send(msg["src"], {**body, "in_reply_to": body["msg_id"]})

    def on(self, typ: str):
        def inner(func):
            if typ in self.handlers:
                raise ValueError(f"Already have a handler for {typ}")

            self.handlers[typ] = func

        return inner

    def main(self):
        for line in sys.stdin:
            msg = self.parse_msg(line)
            self.log(f"Received {msg}")

            with self.lock:
                handler = self.handlers.get(msg["body"]["type"])

                if handler is None:
                    raise Exception(f"No handler for {msg['body']['type']}")

                try:
                    handler(self, msg)
                except Exception as e:
                    self.log(f"Exception handling {msg}\n{e}")


class Broadcast:
    def __init__(
        self,
    ):
        self.node = Node()
        self.neighbors = []
        self.messages = []
        self.lock = Lock()

        @self.node.on("init")
        def initial_handler(node: "Node", msg: Message) -> None:
            body = msg["body"]

            if "node_id" not in body or "node_ids" not in body:
                raise

            node.node_id = body["node_id"]
            node.node_ids = body["node_ids"]

            node.reply(msg, {"type": "init_ok"})
            node.log(f"Node {node.node_id} initialized")

        @self.node.on("topology")
        def topology_handler(node: "Node", msg: Message) -> None:
            body = msg["body"]

            if "topology" not in body:
                raise ValueError("Expected topology key for topology handler in body.")

            self.neighbors = body["topology"][node.node_id]
            node.log(f"My neighbors are {self.neighbors}")
            node.reply(msg, {"type": "topology_ok"})

        @self.node.on("read")
        def read_handler(node: "Node", msg: Message) -> None:
            with self.lock:
                node.reply(msg, {"type": "read_ok", "messages": self.messages})

        @self.node.on("broadcast")
        def broadcast_handler(node: "Node", msg: Message) -> None:
            body = msg["body"]

            if "message" not in body:
                raise ValueError(f"Expected message to be not in body.")

            with self.lock:
                self.messages.append(body["message"])

            node.reply(msg, {"type": "broadcast_ok"})


if __name__ == "__main__":
    broadcast = Broadcast()
    broadcast.node.main()
