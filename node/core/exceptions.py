from pydantic.error_wrappers import ValidationError as PydanticValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError


def convert_to_drf_validation_error(exception: PydanticValidationError):
    errors = {}
    for error in exception.errors():
        errors['.'.join(error['loc'])] = [error['msg']]

    return DRFValidationError(errors)
