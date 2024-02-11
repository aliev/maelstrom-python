#!/usr/bin/env python

from typing import IO, TYPE_CHECKING
import json
import sys
from maelstrom.protocol import Message, Body


class EchoServer:
    def __init__(
        self,
        request: IO[str],
        response: IO[str],
        response_error: IO[str],
        node_id: str | None = None,
    ):
        self.node_id = node_id
        self.next_msg_id = 0

        self.request = request
        self.response = response
        self.response_error = response_error

    def reply(
        self,
        request_message: Message,
        body: Body,
    ):
        self.next_msg_id += 1

        if TYPE_CHECKING:
            assert self.node_id is not None

        response_message: Message = {
            "src": self.node_id,
            "dest": request_message["src"],
            "body": {
                "msg_id": self.next_msg_id,
                "in_reply_to": request_message["body"]["msg_id"],
                **body,
            }
        }

        json.dump(response_message, self.response)

        self.response.write("\n")
        self.response.flush()

    def run(self):
        for line in self.request:
            req = json.loads(line)

            body = req["body"]

            if body["type"] == "init":
                node_id = body["node_id"]
                self.node_id = node_id
                self.response_error.write(f"Initialized node {self.node_id}\n")
                self.reply(req, {"type": "init_ok"})

            if body["type"] == "echo":
                self.response_error.write(f"Echoing {body}")
                self.reply(req, {**body, "type": "echo_ok"})


if __name__ == "__main__":
    s = EchoServer(
        request=sys.stdin,
        response=sys.stdout,
        response_error=sys.stderr,
    )
    s.run()
