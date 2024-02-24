import asyncio
import json
import logging
import sys

from aioshutdown import SIGHUP, SIGINT, SIGTERM

from maelstrom.broadcast import Broadcast
from maelstrom.node import Node
from maelstrom.protocol import Message
from maelstrom.utils import open_io_stream

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s,%(msecs)d %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)


node = Node()
b = Broadcast(node=node)


@node.on()
async def init(node: Node, msg: Message):
    body = msg.get("body", {})
    node_id = body.get("node_id")
    node_ids = body.get("node_ids")

    if node_id is None or node_ids is None:
        return

    node.node_id = node_id
    node.node_ids.update(node_ids)

    await node.log(f"Initialized node '{node.node_id}'")

    await node.reply(msg, {"type": "init_ok"})
    await node.log(f"Node {node.node_id} initialized.")


@node.on()
async def echo(node: Node, msg: Message):
    body = msg.get("body", {})
    node_id = body.get("node_id")
    await node.log(f"Echoing '{node_id}'")
    await node.reply(msg, {"type": "echo_ok", "echo": body.get("echo", "")})


@node.on()
async def topology(node: Node, msg: Message):
    """A topology message informs the node of an (optional) network topology: a map of nodes to neighbors."""
    body = msg.get("body", {})
    topology = body.get("topology", {})
    neighbors = topology.get(node.node_id, [])

    b.neighbors = neighbors

    await node.reply(msg, {"type": "topology_ok"})


@node.on()
async def read(node: Node, msg: Message):
    await node.reply(msg, {"type": "read_ok", "messages": list(b.messages)})


@node.on()
async def broadcast(node: Node, msg: Message):
    """A broadcast request sends a message into the network."""
    body = msg.get("body", {})
    message = body.get("message")
    msg_id = body.get("msg_id")

    # We should avoid broadcasting a message if we already have it
    if message is not None and message not in b.messages:

        # Whenever we receive a broadcast message, we'll add that message's message to the set.
        b.messages.add(message)

        # Gossip this message to neighbors
        for neighbor in b.neighbors:
            # Do not broadcast a message back to the server which sent it to us.
            if msg["src"] == neighbor:
                continue
            await node.send(neighbor, {"type": "broadcast", "message": message})

    # Inter-server messages don't have a msg_id, and don't need a response
    if msg_id is not None:
        await node.reply(msg, {"type": "broadcast_ok"})


async def main():
    try:
        reader_stdin, writer_stdout = await open_io_stream(
            [sys.stdin], [sys.stdout, sys.stderr]
        )

        reader, *_ = reader_stdin
        writer, writer_stderr, *_ = writer_stdout

        node.set_io(reader, writer, writer_stderr)

        async with asyncio.TaskGroup() as tg:
            async for line in reader:
                try:
                    message: Message = json.loads(line)
                except json.decoder.JSONDecodeError as exc:
                    await node.log(str(exc))
                    continue

                await node.log(f"Replying to message {message}")

                body = message.get("body", {})
                typ = body.get("type")
                in_reply_to = body.get("in_reply_to")

                if in_reply_to:
                    handler = node.callbacks[in_reply_to]
                    del node.callbacks[in_reply_to]
                elif typ:
                    handler = node.handlers[typ]
                else:
                    await node.log("Invalid message format")
                    continue

                tg.create_task(handler(node, message))
    except asyncio.CancelledError:
        ...


def run():
    with SIGTERM | SIGHUP | SIGINT as loop:
        task = loop.create_task(main())
        loop.run_until_complete(asyncio.gather(task))
