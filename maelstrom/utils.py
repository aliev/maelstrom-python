import asyncio
import os
from typing import TextIO


async def open_io_stream(
    readers: list[TextIO],
    writers: list[TextIO],
    loop: asyncio.AbstractEventLoop | None = None,
) -> tuple[list[asyncio.StreamReader], list[asyncio.StreamWriter]]:
    """Asynchronously opens IO streams for a list of TextIO objects.

    This function facilitates asynchronous interaction with IO streams, such as stdin, stdout, and stderr, by leveraging
    asyncio's capabilities to avoid blocking operations and the need for separate threads for reading or writing. The
    inclusion of multiple writers allows operations with both stdout and stderr asynchronously.

    NOTE: this function employs asyncio's IO multiplexing, which allows for efficient IO operations by
    monitoring multiple file descriptors simultaneously without the overhead of creating separate threads.
    """
    readers_lst = []
    writers_lst = []

    if loop is None:
        loop = asyncio.get_running_loop()

    for reader in readers:
        # Create a StreamReader and protocol pair
        _reader = asyncio.StreamReader(loop=loop)
        protocol = asyncio.StreamReaderProtocol(_reader)

        # Connect the reader to stdin
        # Source: https://stackoverflow.com/questions/58454190/python-async-waiting-for-stdin-input-while-doing-other-stuff
        await loop.connect_read_pipe(lambda: protocol, reader)
        readers_lst.append(_reader)

    for writer in writers:
        # Source: https://stackoverflow.com/questions/52089869/how-to-create-asyncio-stream-reader-writer-for-stdin-stdout
        writer_transport, writer_protocol = await loop.connect_write_pipe(
            lambda: asyncio.streams.FlowControlMixin(loop=loop),
            os.fdopen(writer.fileno(), "wb"),
        )

        _writer = asyncio.streams.StreamWriter(
            writer_transport, writer_protocol, None, loop
        )
        writers_lst.append(_writer)

    return readers_lst, writers_lst
