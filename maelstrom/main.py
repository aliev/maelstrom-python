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
async def init(node: Node, request: Message):
    await asyncio.sleep(1000)


@node.on("topology")
async def topology(node: Node, request: Message):
    ...


@node.on("broadcast")
async def broadcast(node: Node, request: Message):
    ...


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
                tg.create_task(node.handlers[message["body"]["type"]](node, message))

    except asyncio.CancelledError:
        ...
