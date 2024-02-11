from maelstrom.node import Node


class Broadcast:
    def __init__(
        self,
        node: Node,
    ):
        self.node = node
        self.neighbors: list[str] = []
        self.messages: set[int] = set()
