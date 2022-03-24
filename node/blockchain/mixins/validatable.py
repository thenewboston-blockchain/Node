class ValidatableMixin:

    def validate_business_logic(self):  # validate() is used by pydantic there we use a longer name
        raise NotImplementedError('Must be implemented in child class')

    def validate_blockchain_state_dependent(self, blockchain_facade, **kwargs):
        raise NotImplementedError('Must be implemented in child class')

    def validate_all(self, blockchain_facade, **kwargs):
        self.validate_business_logic()
        self.validate_blockchain_state_dependent(blockchain_facade, **kwargs)
