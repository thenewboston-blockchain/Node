from django.core.exceptions import ValidationError as DjangoValidationError
from pydantic import ValidationError as PydanticValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError


class DRFValidationErrorConverter(DRFValidationError):

    def __init__(self, exception, *args, **kwargs):
        convert_exception = self.get_convertor(exception)
        super().__init__(convert_exception(exception), *args, **kwargs)

    def get_convertor(self, exception):
        if isinstance(exception, PydanticValidationError):
            return self.convert_pydantic_validation_error
        elif isinstance(exception, ValidationError):
            return self.convert_validation_error
        else:
            raise NotImplementedError

    def convert_pydantic_validation_error(self, exception: PydanticValidationError):
        errors = {}
        for error in exception.errors():
            loc = error['loc']
            key = 'non_field_errors' if loc == ('__root__',) else '.'.join(map(str, loc))
            errors[key] = [error['msg']]
        return errors

    def convert_validation_error(self, exception: 'ValidationError'):
        non_field_errors = [e.message for e in exception.error_list]
        return dict(non_field_errors=non_field_errors)


class ValidationError(DjangoValidationError):
    pass


class NotEnoughNestingError(ValueError):
    pass
