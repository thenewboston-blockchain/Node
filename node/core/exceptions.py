from django.core.exceptions import ValidationError as DjangoValidationError
from pydantic import ValidationError as PydanticValidationError
from rest_framework.exceptions import APIException
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.fields import get_error_detail
from rest_framework.views import exception_handler


def convert_pydantic_validation_error(exception: PydanticValidationError):
    errors = {}
    for error in exception.errors():
        loc = error['loc']
        key = 'non_field_errors' if loc == ('__root__',) else '.'.join(map(str, loc))
        errors[key] = [error['msg']]
    return DRFValidationError(errors)


def convert_django_validation_error(exception: DjangoValidationError):
    details = get_error_detail(exception)
    if not isinstance(details, dict):
        details = {'non_field_errors': details}
    return DRFValidationError(details)


def custom_exception_handler(exc, context):
    if isinstance(exc, PydanticValidationError):
        exc = convert_pydantic_validation_error(exc)
    elif isinstance(exc, DjangoValidationError):
        exc = convert_django_validation_error(exc)

    if isinstance(exc, APIException):
        # Adding machine readable error code.
        # Original implementation copied from https://stackoverflow.com/a/50301325/1952977
        exc.detail = exc.get_full_details()

    return exception_handler(exc, context)


class ValidationError(DjangoValidationError):
    pass


class NotEnoughNestingError(ValueError):
    pass


class NodeError(Exception):
    pass


class BlockchainError(NodeError):
    pass


class BlockchainSyncError(NodeError):
    pass


class BlockchainLockingError(BlockchainError):
    pass


class BlockchainIsNotLockedError(BlockchainError):
    pass


class BlockchainUnlockingError(BlockchainError):
    pass


class DatabaseTransactionError(NodeError):
    pass
