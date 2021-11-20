from node.core.utils.types import Type

from .genesis import GenesisBlockMessage
from .node_declaration import NodeDeclarationBlockMessage

TYPE_MAP = {Type.GENESIS: GenesisBlockMessage, Type.NODE_DECLARATION: NodeDeclarationBlockMessage}
