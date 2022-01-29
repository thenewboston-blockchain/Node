from djongo.models.fields import DjongoManager

from node.core.managers import CustomQuerySet

from .account_state import AccountState


class NodeManager(DjongoManager.from_queryset(CustomQuerySet)):  # type: ignore

    def get_queryset(self):
        return super().get_queryset().filter(node__isnull=False)


class Node(AccountState):

    objects = NodeManager()

    class Meta:
        proxy = True

    def get_node_attribute(self, name):
        return (self.node or {}).get(name)

    @property
    def identifier(self):
        return self._id

    @property
    def addresses(self):
        return self.get_node_attribute('addresses')

    @property
    def fee(self):
        return self.get_node_attribute('fee')
