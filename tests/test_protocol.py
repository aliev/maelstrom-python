import pytest
from maelstrom.protocol import Body, Message

def test_body_typing():
    body = Body(type="test", msg_id=1, node_id="node1")
    assert body["type"] == "test"
    assert body["msg_id"] == 1
    assert body["node_id"] == "node1"

def test_message_typing():
    body = Body(type="test", msg_id=1, node_id="node1")
    message = Message(src="node1", dest="node2", body=body)
    assert message["src"] == "node1"
    assert message["dest"] == "node2"
    assert message["body"] == body
