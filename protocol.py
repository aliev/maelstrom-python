from typing import Any, NotRequired, TypedDict


class Body(TypedDict):
    type: str
    """
    A string identifying the type of message this is
    """

    msg_id: NotRequired[str]
    """
    A unique integer identifier
    """
    in_reply_to: NotRequired[str]
    """
    For req/response, the msg_id of the request
    """

    node_id: NotRequired[int]
    """
    Indicates the ID of the node which is receiving this message
    """

    node_ids: NotRequired[list[int]]
    """
    Lists all nodes in the cluster, including the recipient
    """

    message: NotRequired[str]


class Message(TypedDict):
    src: str
    """
    A string identifying the node this message came from
    """
    dest: str
    """
    A string identifying the node this message is to
    """
    body: Body
    """
    An object: the payload of the message
    """
