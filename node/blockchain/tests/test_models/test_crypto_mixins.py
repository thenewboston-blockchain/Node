from node.blockchain.inner_models.base import BaseModel
from node.blockchain.mixins.crypto import CryptoAuxiliaryMixin


def test_make_binary_data_for_cryptography_key_order():

    class Inner(BaseModel):
        key2: str
        key1: str

    class Outer(BaseModel, CryptoAuxiliaryMixin):
        key3: Inner
        key2: str
        key1: int

    inner = Inner(key2='v2', key1='v1')
    outer = Outer(key3=inner, key2='v2', key1=1)

    # is cryptographic friendly by default
    assert outer.json() == '{"key1":1,"key2":"v2","key3":{"key1":"v1","key2":"v2"}}'

    # ordered key for cryptography
    assert outer.make_binary_representation_for_cryptography(
    ) == b'{"key1":1,"key2":"v2","key3":{"key1":"v1","key2":"v2"}}'
