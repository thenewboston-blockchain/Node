import pytest

from node.blockchain.models.block import Block


@pytest.mark.django_db
def test_block_sequence():
    block = Block(_id=0, body='fake')
    block.save()
    block = Block(_id=0, body='fake')
    with pytest.raises(ValueError, match='Expected block_id is 1'):
        block.save()

    block._id = 1
    block.save()
