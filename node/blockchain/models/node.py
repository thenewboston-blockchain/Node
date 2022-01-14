from .account_state import AccountState


class Node(AccountState):

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
