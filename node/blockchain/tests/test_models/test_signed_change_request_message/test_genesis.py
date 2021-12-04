from node.blockchain.inner_models import GenesisSignedChangeRequestMessage
from node.blockchain.inner_models.signed_change_request_message.genesis import AlphaAccount
from node.core.utils.types import AccountLock, Type


def test_create_from_treasury_account(primary_validator_key_pair, treasury_account_key_pair, treasury_amount):
    message = GenesisSignedChangeRequestMessage.create_from_treasury_account(
        account_lock=AccountLock(primary_validator_key_pair.public),
        treasury_account_number=treasury_account_key_pair.public,
        treasury_amount=treasury_amount
    )
    assert message.type == Type.GENESIS
    assert message.account_lock == AccountLock(primary_validator_key_pair.public)
    assert len(message.accounts) == 1
    assert message.accounts == {
        treasury_account_key_pair.public:
            AlphaAccount(balance=treasury_amount, balance_lock=treasury_account_key_pair.public)
    }


def test_create_from_alpha_account_root_file(primary_validator_key_pair, account_root_file):
    message = GenesisSignedChangeRequestMessage.create_from_alpha_account_root_file(
        account_lock=AccountLock(primary_validator_key_pair.public),
        account_root_file=account_root_file,
    )
    assert message.type == Type.GENESIS
    assert message.account_lock == AccountLock(primary_validator_key_pair.public)
    assert len(message.accounts) == len(account_root_file)
    assert message.accounts.keys() == account_root_file.keys()
    assert message.accounts == {
        key: AlphaAccount(balance=value['balance'], balance_lock=value['balance_lock'])
        for key, value in account_root_file.items()
    }


def test_serialize_to_dict_for_cryptography(genesis_signed_change_request_message):
    serialized = genesis_signed_change_request_message.make_binary_message_for_cryptography()
    accounts = genesis_signed_change_request_message.accounts
    assert len(accounts) == 1
    account_number, account = accounts.popitem()

    assert serialized == (
        '{"account_lock":"%s","accounts":{"%s":{"balance":%s,"balance_lock":"%s"}},"type":0}' % (
            genesis_signed_change_request_message.account_lock,
            account_number,
            account.balance,
            account.balance_lock,
        )
    ).encode('utf-8')


def test_serialize_deserialize_works(genesis_signed_change_request_message):
    serialized = genesis_signed_change_request_message.json()
    deserialized = GenesisSignedChangeRequestMessage.parse_raw(serialized)
    assert deserialized == genesis_signed_change_request_message

    serialized2 = deserialized.json()
    assert serialized == serialized2
