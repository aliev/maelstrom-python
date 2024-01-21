#!/usr/bin/env python

import json
import sys
from typing import IO, Any, Callable
from multiprocessing import Lock, RLock
from protocol import Message


Handler = Callable[["Node", Message], None]


def initial_handler(node: "Node", msg: Message) -> None:
    node.node_id = msg["body"]["node_id"]
    node.node_ids = msg["body"]["node_ids"]

    node.reply(msg, {"type": "init_ok"})
    node.log(f"Node {node.node_id} initialized")



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

        self.on("init", initial_handler)

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


    def reply(self, req: Message, body: dict[str, Any]):
        body = {**body, "in_reply_to": req["body"]["msg_id"]}

        self.send(req["src"], body)

    def on(self, typ: str, handler: Handler):
        if handler in self.handlers:
            raise ValueError(f"Already have a handler for {typ}")

        self.handlers[typ] = handler

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
        self.messages = set()
        self.lock = Lock()

        def topology_handler(node: "Node", msg: Message) -> None:
            self.neighbors = msg["body"]["topology"][node.node_id]
            node.log(f"My neighbors are {self.neighbors}")
            node.reply(msg, {"type": "topology_ok"})

        def read_handler(node: "Node", msg: Message) -> None:
            with self.lock:
                node.reply(msg, {"type": "read_ok", "messages": self.messages})

        def broadcast_handler(node: "Node", msg: Message) -> None:
            m = msg["body"]["message"]

            with self.lock:
                self.messages.add(m)

            node.reply(msg, {"type": "broadcast_ok"})


        self.node.on("topology", topology_handler)
        self.node.on("read", read_handler)
        self.node.on("broadcast", broadcast_handler)


if __name__ == "__main__":
    broadcast = Broadcast()
    broadcast.node.main()
