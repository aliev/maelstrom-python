from typing import NotRequired, TypedDict


class Body(TypedDict):
    type: str
    """
    A string identifying the type of message.
    """

    msg_id: NotRequired[int]
    """
    A unique integer identifier
    """
    in_reply_to: NotRequired[int]
    """
    For req/response, the msg_id of the request
    """

    node_id: NotRequired[str]
    """
    Indicates the ID of the node which is receiving this message
    """

    node_ids: NotRequired[list[str]]
    """
    Lists all nodes in the cluster, including the recipient
    """

    message: NotRequired[int]

    messages: NotRequired[list]

    topology: NotRequired[dict[str, list[str]]]

    echo: NotRequired[str]


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
