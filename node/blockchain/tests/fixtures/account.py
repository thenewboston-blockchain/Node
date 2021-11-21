import pytest

from node.core.utils.types import AccountNumber, KeyPair, SigningKey


@pytest.fixture
def treasury_account_key_pair() -> KeyPair:
    return KeyPair(
        public=AccountNumber('4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732'),
        private=SigningKey('1104d51eb539e66fa108f99d18ab179aa98c10678961821ddd87bfdbf351cb79'),
    )


@pytest.fixture
def primary_validator_key_pair() -> KeyPair:
    return KeyPair(
        public=AccountNumber('b9dc49411424cce606d27eeaa8d74cb84826d8a1001d17603638b73bdc6077f1'),
        private=SigningKey('98d6b2744d93245e48e336b7d24a316947005b00805c776cff9946109c194675'),
    )


@pytest.fixture
def regular_node_key_pair() -> KeyPair:
    return KeyPair(
        public=AccountNumber('1c8e5f54a15b63a9f3d540ce505fd0799575ffeaac62ce625c917e6d915ea8bb'),
        private=SigningKey('d0a03fea134f3f83901f36071f79026b2224a7f926546486f72104351dc23432'),
    )


@pytest.fixture
def user_key_pair() -> KeyPair:
    return KeyPair(
        public=AccountNumber('97b369953f665956d47b0a003c268ad2b05cf601b8798210ca7c2423afb9af78'),
        private=SigningKey('f450b3082201544bc9348e862b818d3423857c0eb7bec5d00751098424186454'),
    )
