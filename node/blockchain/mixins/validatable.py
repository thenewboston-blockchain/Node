class ValidatableMixin:

    def validate_business_logic(self):  # validate() is used by pydantic
        pass

    def validate_blockchain_state_dependent(self, blockchain_facade):
        pass
