import asyncio
import json
import logging
import sys
from maelstrom.node import Node
from maelstrom.broadcast import Broadcast
from maelstrom.protocol import Message
from maelstrom.utils import open_io_stream

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s,%(msecs)d %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)


node = Node()
b = Broadcast(node=node)

@node.on("init")
async def init(node: Node, msg: Message):
    body = msg.get("body", {})
    node_id = body.get("node_id")
    node_ids = body.get("node_ids")

    if node_id is None or node_ids is None:
        return

    node.node_id = node_id
    node.node_ids.update(node_ids)

    await node.reply(msg, {"type": "init_ok"})
    await node.log(f"Node {node.node_id} initialized.")


@node.on("echo")
async def echo(node: Node, msg: Message):
    body = msg.get("body", {})
    await node.log(f"Echoing '{body.get("node_id")}'")
    await node.reply(msg, {"type": "echo_ok", "echo": body.get("echo", "")})

@node.on("topology")
async def topology(node: Node, msg: Message):
    body = msg.get("body", {})
    neighbors = body.get("topology", {}).get(node.node_id, [])
    b.neighbors = neighbors
    await node.reply(msg, {"type": "topology_ok"})


@node.on("read")
async def read(node: Node, msg: Message):
    await node.reply(msg, {"type": "read_ok", "messages": list(b.messages)})


@node.on("broadcast")
async def broadcast(node: Node, msg: Message):
    body = msg.get("body", {})
    message = body.get("message")

    if message is None:
        return

    b.messages.add(message)

    # Gossip this message to neighbors
    for neighbor in b.neighbors:
        await node.send(neighbor, {"type": "broadcast", "message": message})

    await node.reply(msg, {"type": "broadcast_ok"})


async def main():
    try:
        reader_stdin, writer_stdout = await open_io_stream([sys.stdin], [sys.stdout, sys.stderr])

        reader, *_ = reader_stdin
        writer, writer_stderr, *_ = writer_stdout

        node.set_io(reader, writer, writer_stderr)

        async with asyncio.TaskGroup() as tg:
            async for line in reader:
                try:
                    message: Message = json.loads(line)
                except json.decoder.JSONDecodeError:
                    continue

                await node.log(f"Replying to message {message}")

                tg.create_task(node.handlers[message["body"]["type"]](node, message))

    except asyncio.CancelledError:
        ...
