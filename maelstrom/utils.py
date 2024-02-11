import asyncio
import os
from typing import TextIO


async def open_io_stream(
    readers: list[TextIO],
    writers: list[TextIO],
) -> tuple[list[asyncio.StreamReader], list[asyncio.StreamWriter]]:
    loop = asyncio.get_running_loop()
    readers_lst = []
    writers_lst = []

    for reader in readers:
        # Create a StreamReader and protocol pair
        _reader = asyncio.StreamReader(loop=loop)
        protocol = asyncio.StreamReaderProtocol(_reader)

        # Connect the reader to stdin
        # NOTE: https://stackoverflow.com/questions/58454190/python-async-waiting-for-stdin-input-while-doing-other-stuff
        await loop.connect_read_pipe(lambda: protocol, reader)
        readers_lst.append(_reader)

    for writer in writers:
        # NOTE: https://stackoverflow.com/questions/52089869/how-to-create-asyncio-stream-reader-writer-for-stdin-stdout
        writer_transport, writer_protocol = await loop.connect_write_pipe(
            lambda: asyncio.streams.FlowControlMixin(loop=loop),
            os.fdopen(writer.fileno(), "wb"))

        _writer = asyncio.streams.StreamWriter(writer_transport, writer_protocol, None, loop)
        writers_lst.append(_writer)


    return readers_lst, writers_lst
