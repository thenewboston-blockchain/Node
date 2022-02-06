class ValidatableMixin:

    def validate_business_logic(self):  # validate() is used by pydantic
        raise NotImplementedError('Must be implemented in child class')

    def validate_blockchain_state_dependent(self, blockchain_facade):
        raise NotImplementedError('Must be implemented in child class')
