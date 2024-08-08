import pytest
from maelstrom.main import node, b, create_handler, init, echo, topology, read, broadcast

@pytest.fixture
def mock_node():
    class MockNode:
        def __init__(self):
            self.handlers = {}
            self.callbacks = {}
            self.node_id = ""
            self.node_ids = set()
            self.next_msg_id = 0

        def on(self, name=None):
            def inner(handler):
                handler_name = handler.__name__ if name is None else name
                self.handlers[handler_name] = handler
            return inner

        async def reply(self, msg, body):
            pass

        async def log(self, msg, *args):
            pass

        async def rpc(self, dest, body, handler):
            pass

    return MockNode()

@pytest.mark.asyncio
async def test_init(mock_node):
    msg = {"body": {"node_id": "node1", "node_ids": ["node1", "node2"]}}
    await init(mock_node, msg)
    assert mock_node.node_id == "node1"
    assert mock_node.node_ids == {"node1", "node2"}

@pytest.mark.asyncio
async def test_echo(mock_node):
    msg = {"body": {"node_id": "node1", "echo": "hello"}}
    await echo(mock_node, msg)
    assert mock_node.node_id == "node1"

@pytest.mark.asyncio
async def test_topology(mock_node):
    msg = {"body": {"topology": {"node1": ["node2", "node3"]}}}
    await topology(mock_node, msg)
    assert b.neighbors == ["node2", "node3"]

@pytest.mark.asyncio
async def test_read(mock_node):
    msg = {}
    await read(mock_node, msg)
    assert True  # Just to ensure the function runs without error

@pytest.mark.asyncio
async def test_broadcast(mock_node):
    msg = {"body": {"message": 1}, "src": "node1"}
    await broadcast(mock_node, msg)
    assert 1 in b.messages
