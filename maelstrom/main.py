import asyncio
import json
import logging
import sys
from ast import Call
from typing import Callable

from aioshutdown import SIGHUP, SIGINT, SIGTERM

from maelstrom.broadcast import Broadcast
from maelstrom.node import Node
from maelstrom.protocol import Message
from maelstrom.utils import open_io_stream_reader, open_io_stream_writer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s,%(msecs)d %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)


node = Node()
b = Broadcast(node=node)


def create_callback(unacked: list[str], dest: str):
    async def handler(node: Node, res: Message):
        if res["body"]["type"] == "broadcast_ok":
            if dest in unacked:
                unacked.remove(dest)

    return handler


@node.on()
async def init(node: Node, msg: Message):
    body = msg.get("body", {})
    node_id = body.get("node_id")
    node_ids = body.get("node_ids")

    if node_id is None or node_ids is None:
        return

    node.node_id = node_id
    node.node_ids.update(node_ids)

    await node.log("Initialized node '%s'", node.node_id)

    await node.reply(msg, {"type": "init_ok"})
    await node.log("Node %s initialized.", node.node_id)


@node.on()
async def echo(node: Node, msg: Message):
    body = msg.get("body", {})
    node_id = body.get("node_id")
    await node.log("Echoing '%s'", node_id)
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

    # Acknowledge the request
    await node.reply(msg, {"type": "broadcast_ok"})

    # Do we need to process this message?
    body = msg.get("body")

    if body is None:
        await node.log("Mailformed message. body cannot be empty.")
        return

    m = body.get("message")

    if m is None:
        return

    new_message = False

    if m not in b.messages:
        b.messages.add(m)
        new_message = True

    if new_message:
        unacked = b.neighbors.copy()

        while unacked:
            await node.log("Need to replicate %d to %s", m, unacked)

            for dest in unacked:
                await node.rpc(
                    dest=dest,
                    body=body,
                    handler=create_callback(unacked=unacked, dest=dest),
                )

            await asyncio.sleep(1)


async def loop(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    logger: asyncio.StreamWriter,
):
    node.set_io(reader, writer, logger)

    async with asyncio.TaskGroup() as tg:
        async for line in reader:
            try:
                message: Message = json.loads(line)
            except json.decoder.JSONDecodeError as exc:
                await node.log(str(exc))
                continue

            await node.log("Replying to message '%s'", message)

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


async def main():
    try:
        reader = await open_io_stream_reader(sys.stdin)
        writer = await open_io_stream_writer(sys.stdout)
        logger = await open_io_stream_writer(sys.stderr)

        await loop(reader, writer, logger)
    except asyncio.CancelledError:
        ...


def run():
    with SIGTERM | SIGHUP | SIGINT as loop:
        task = loop.create_task(main())
        loop.run_until_complete(asyncio.gather(task))
