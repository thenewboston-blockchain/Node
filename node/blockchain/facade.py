import logging
from typing import TYPE_CHECKING, Optional, Type, TypeVar  # noqa: I101

from node.blockchain.constants import BLOCK_LOCK
from node.blockchain.inner_models import Block, BlockMessage, Node, SignedChangeRequest
from node.blockchain.mixins.crypto import HashableStringWrapper
from node.blockchain.models import AccountState as ORMAccountState
from node.blockchain.models import Node as ORMNode
from node.blockchain.types import AccountLock, AccountNumber, BlockIdentifier, NodeRole, SigningKey
from node.blockchain.utils.lock import lock
from node.core.database import ensure_in_transaction
from node.core.utils.cryptography import derive_public_key, get_node_identifier, get_signing_key
from node.core.utils.misc import set_if_not_none
from node.core.utils.types import intstr

if TYPE_CHECKING:
    from node.blockchain.models import Block as ORMBlock

T = TypeVar('T', bound='BlockchainFacade')

logger = logging.getLogger(__name__)


def get_block_model():
    # We need it to resolve circular imports
    from node.blockchain.models import Block
    return Block


class BlockchainFacade:

    _instance = None

    def __init__(self, signing_key: SigningKey):
        self.signing_key = signing_key

    @classmethod
    def get_instance(cls: Type[T]) -> T:
        instance = cls._instance
        if not instance:
            instance = cls(signing_key=get_signing_key())
            cls.set_instance_cache(instance)

        return instance

    @classmethod
    def set_instance_cache(cls: Type[T], instance: T):
        cls._instance = instance

    @classmethod
    def clear_instance_cache(cls):
        cls._instance = None

    @ensure_in_transaction
    @lock(BLOCK_LOCK)
    def add_block_from_json(self, block_json: str) -> 'ORMBlock':
        return self.add_block(Block.parse_raw(block_json), expect_locked=True)

    @ensure_in_transaction
    @lock(BLOCK_LOCK)
    def add_block_from_dict(self, block_dict: dict) -> 'ORMBlock':
        return self.add_block(Block.parse_obj(block_dict), expect_locked=True)

    @ensure_in_transaction
    @lock(BLOCK_LOCK)
    def add_block(self, block: Block, *, validate=True) -> 'ORMBlock':
        if validate:
            block.validate_business_logic()

        # Make blockchain state specific validations
        block.validate_blockchain_state_dependent(self, bypass_lock_validation=True)

        from node.blockchain.models import Block as ORMBlock
        orm_block = ORMBlock(_id=block.message.number, body=block.json())
        orm_block.save()

        self.update_write_through_cache(block)
        return orm_block

    @ensure_in_transaction
    @lock(BLOCK_LOCK)
    def add_block_from_block_message(
        self,
        message: BlockMessage,
        *,
        signing_key: Optional[SigningKey] = None,
        validate=True,
    ) -> Block:
        if validate:
            message.validate_business_logic()

        signing_key = signing_key or get_signing_key()
        signer = derive_public_key(signing_key)
        signature = message.make_signature(signing_key)

        block = Block(signer=signer, signature=signature, message=message)
        # No need to validate the block since we produced a valid one
        self.add_block(block, validate=False, expect_locked=True)
        return block

    @ensure_in_transaction
    @lock(BLOCK_LOCK)
    def add_block_from_signed_change_request(
        self,
        signed_change_request: SignedChangeRequest,
        *,
        signing_key: Optional[SigningKey] = None,
        validate=True
    ) -> Block:
        if validate:
            signed_change_request.validate_business_logic()

        block_message = BlockMessage.create_from_signed_change_request(signed_change_request, self)
        # no need to validate the block message since we produced a valid one
        return self.add_block_from_block_message(
            block_message, signing_key=signing_key, validate=False, expect_locked=True
        )

    @staticmethod
    def get_block_count():
        return get_block_model().objects.count()

    @staticmethod
    def has_blocks():
        return get_block_model().objects.exists()

    @staticmethod
    def get_last_block():
        return get_block_model().objects.get_last_block()

    def get_next_block_number(self) -> int:
        # TODO(dmu) HIGH: Implement method via write-through cache
        #                 https://thenewboston.atlassian.net/browse/BC-175
        last_block = self.get_last_block()
        return last_block._id + 1 if last_block else 0

    def get_next_block_identifier(self) -> Optional[BlockIdentifier]:
        # TODO(dmu) HIGH: Implement method via write-through cache
        #                 https://thenewboston.atlassian.net/browse/BC-175
        last_block = self.get_last_block()
        if not last_block:
            return None

        return HashableStringWrapper(last_block.body).make_hash()

    @staticmethod
    def get_account_lock(account_number) -> AccountLock:
        account_state = ORMAccountState.objects.get_or_none(_id=account_number)
        return AccountLock(account_state.account_lock) if account_state else account_number

    @staticmethod
    def get_account_balance(account_number: AccountNumber) -> int:
        account_state = ORMAccountState.objects.get_or_none(_id=account_number)
        return account_state.balance if account_state else 0

    @staticmethod
    def update_write_through_cache_accounts(accounts):
        for account_number, account_state in accounts.items():
            fields_for_update = {}
            set_if_not_none(fields_for_update, 'account_lock', account_state.account_lock)
            set_if_not_none(fields_for_update, 'balance', account_state.balance)
            node = None if account_state.node is None else account_state.node.dict()
            set_if_not_none(fields_for_update, 'node', node)
            assert fields_for_update

            account_state, is_created = ORMAccountState.objects.get_or_create(
                _id=account_number, defaults=fields_for_update
            )
            if not is_created:
                for field, value in fields_for_update.items():
                    setattr(account_state, field, value)
                account_state.save()

    @staticmethod
    def update_write_through_cache_schedule(schedule: dict[intstr, AccountNumber]):
        # TODO(dmu) HIGH: Add more unittests once PV schedule block is implemented
        #                 - Add PV
        #                 - Remove PV
        #                 - Replace PV
        #                 https://thenewboston.atlassian.net/browse/BC-193
        from node.blockchain.models import Schedule

        Schedule.objects.exclude(_id__in=schedule.keys()).delete()

        for block_number, node_identifier in schedule.items():
            Schedule.objects.update_or_create(_id=block_number, defaults={'node_identifier': node_identifier})

    @staticmethod
    @ensure_in_transaction
    @lock(BLOCK_LOCK)
    def clear():
        get_block_model().objects.all().delete()

        ORMAccountState.objects.all().delete()
        from node.blockchain.models import Schedule
        Schedule.objects.all().delete()

    def update_write_through_cache(self, block):
        block_message_update = block.message.update

        if accounts := block_message_update.accounts:
            self.update_write_through_cache_accounts(accounts)

        if schedule := block_message_update.schedule:
            self.update_write_through_cache_schedule(schedule)

    @staticmethod
    def get_node_by_identifier(identifier) -> Optional[Node]:
        node = ORMNode.objects.get_or_none(_id=identifier)
        return node.get_node() if node else None

    def get_node_role(self) -> Optional[NodeRole]:
        # TODO(dmu) MEDIUM: Should we optimize the implementation to make only one database request and
        #                   process the response in Python?
        from node.blockchain.models import Schedule

        node_identifier = get_node_identifier()
        node = self.get_node_by_identifier(node_identifier)
        if not node:
            return None

        if not Schedule.objects.filter(node_identifier=node_identifier).exists():
            return NodeRole.REGULAR_NODE

        next_block_number = self.get_next_block_number()
        schedule = Schedule.objects.filter(_id__lte=next_block_number).order_by('-_id').first()
        if schedule and schedule.node_identifier == node_identifier:
            return NodeRole.PRIMARY_VALIDATOR

        if Schedule.objects.filter(_id__gt=next_block_number, node_identifier=node_identifier).exists():
            return NodeRole.CONFIRMATION_VALIDATOR

        return NodeRole.REGULAR_NODE

    def get_primary_validator(self) -> Optional[Node]:
        """
        Return primary validator that should sign the next block
        """
        from node.blockchain.models import Schedule

        schedule = Schedule.objects.filter(_id__lte=self.get_next_block_number()).order_by('-_id').first()
        if not schedule:
            logger.warning('Schedule for the next block was not found')
            return None

        node_identifier = schedule.node_identifier
        node = self.get_node_by_identifier(node_identifier)
        if not node:
            # TODO(dmu) HIGH: Implement workaround for the case when
            #                 node unregisters itself by the moment it is scheduled
            #                 https://thenewboston.atlassian.net/browse/BC-236
            logger.warning('Primary validator %s is in PV schedule but not declared as a node', node_identifier)

        return node
