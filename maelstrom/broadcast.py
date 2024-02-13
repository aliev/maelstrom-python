from maelstrom.node import Node


class Broadcast:
    def __init__(
        self,
        node: Node,
    ):
        self.node = node
        self.neighbors: list[str] = []
        self.messages: set[int] = set()

    async def set_neighbors(self, neighbors: list[str]):
        self.neighbors = neighbors

    async def add_message(self, message: int):
        self.messages.add(message)
