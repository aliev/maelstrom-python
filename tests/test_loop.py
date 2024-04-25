import io

import pytest

from maelstrom.utils import open_io_stream_writer


@pytest.mark.asyncio
async def test_loop():

    res = io.StringIO()

    writer = await open_io_stream_writer(res)

    writer.write(b"Hello, world!")
    await writer.drain()
