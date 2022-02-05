from node.core.managers import CustomManager

BLOCK_LOCK = 'block'


class BlockManager(CustomManager):

    def create(self, *args, **kwargs):
        # This method is blocked intentionally to prohibit adding of invalid blocks
        raise NotImplementedError('One of the `add_block*() methods must be used')

    def get_last_block(self):
        return self.order_by('-_id').first()
