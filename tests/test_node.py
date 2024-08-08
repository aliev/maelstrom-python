import pytest
from maelstrom.node import Node

@pytest.fixture
def mock_node():
    class MockNode(Node):
        def __init__(self):
            super().__init__()

        async def reply(self, msg, body):
            pass

        async def log(self, msg, *args):
            pass

        async def rpc(self, dest, body, handler):
            pass

    return MockNode()

@pytest.mark.asyncio
async def test_node_initialization(mock_node):
    assert mock_node.node_id == ""
    assert mock_node.node_ids == set()
    assert mock_node.next_msg_id == 0

@pytest.mark.asyncio
async def test_node_on(mock_node):
    @mock_node.on("test_handler")
    async def test_handler(node, msg):
        pass

    assert "test_handler" in mock_node.handlers

@pytest.mark.asyncio
async def test_node_rpc(mock_node):
    async def handler(node, msg):
        pass

    await mock_node.rpc("node2", {"type": "test"}, handler)
    assert mock_node.next_msg_id == 1
    assert 1 in mock_node.callbacks

@pytest.mark.asyncio
async def test_node_reply(mock_node):
    msg = {"src": "node1", "body": {"msg_id": 1}}
    await mock_node.reply(msg, {"type": "test_reply"})
    assert mock_node.next_msg_id == 1

@pytest.mark.asyncio
async def test_node_log(mock_node):
    await mock_node.log("Test log message")
    assert True  # Just to ensure the function runs without error

@pytest.mark.asyncio
async def test_node_send(mock_node):
    await mock_node.send("node2", {"type": "test_send"})
    assert mock_node.next_msg_id == 0  # Ensure msg_id is not incremented on send
