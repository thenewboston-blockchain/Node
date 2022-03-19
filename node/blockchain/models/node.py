from typing import Collection

from djongo.models.fields import DjongoManager

from node.blockchain.inner_models import Node as PydanticNode
from node.blockchain.types import NodeRole
from node.core.managers import CustomQuerySet

from .account_state import AccountState

NODE_ROLES = set(NodeRole)


class NodeQuerySet(CustomQuerySet):

    def filter_by_roles(self, roles: Collection[NodeRole]):
        # self.annotate() does not work with Djongo
        if not roles:
            return self.none()

        roles = set(roles)
        if roles == NODE_ROLES:
            return self

        assert not (roles - NODE_ROLES)

        from node.blockchain.models import Schedule

        assert {NodeRole.REGULAR_NODE, NodeRole.CONFIRMATION_VALIDATOR, NodeRole.PRIMARY_VALIDATOR} == NODE_ROLES

        next_block_schedule = Schedule.objects.get_schedule_for_next_block()
        primary_validator_identifier = next_block_schedule.node_identifier if next_block_schedule else None
        validator_identifiers = {item.node_identifier for item in Schedule.objects.all().order_by('_id')}
        if NodeRole.REGULAR_NODE in roles:
            if NodeRole.PRIMARY_VALIDATOR in roles:
                if NodeRole.CONFIRMATION_VALIDATOR in roles:
                    raise AssertionError('Should have exited on previous shortcut guard condition')
                else:  # regular and primary validator
                    return self.exclude(_id__in=validator_identifiers - {primary_validator_identifier})
            elif NodeRole.CONFIRMATION_VALIDATOR in roles:  # regular and confirmation
                return self.exclude(_id=primary_validator_identifier)
            else:  # only regular
                return self.exclude(_id__in=validator_identifiers)

        if NodeRole.PRIMARY_VALIDATOR in roles:
            if NodeRole.CONFIRMATION_VALIDATOR in roles:  # only all validators
                return self.filter(_id__in=validator_identifiers)
            else:  # only primary validator
                return self.filter(_id=primary_validator_identifier)
        elif NodeRole.CONFIRMATION_VALIDATOR in roles:  # only confirmation validators
            return self.filter(_id__in=validator_identifiers - {primary_validator_identifier})

        raise AssertionError('Should have exited on previous shortcut guard condition')

    def filter_confirmation_validators(self):
        return self.filter_by_roles((NodeRole.CONFIRMATION_VALIDATOR,))


class NodeManager(DjongoManager.from_queryset(NodeQuerySet)):  # type: ignore

    def get_queryset(self):
        return super().get_queryset().filter(node__isnull=False)

    def is_confirmation_validator(self, identifier):
        return self.filter_by_roles((NodeRole.CONFIRMATION_VALIDATOR,)).filter(_id=identifier).exists()


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

    def get_node(self) -> PydanticNode:
        return PydanticNode(
            identifier=self.identifier,
            addresses=self.addresses,
            fee=self.fee,
        )
