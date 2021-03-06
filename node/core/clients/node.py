import functools
import logging
import sys
from typing import Generator, Optional, Type, TypeVar, Union
from urllib.parse import urlencode, urljoin

import requests

from node.blockchain.inner_models import AccountState, Block, BlockConfirmation, Node, SignedChangeRequest
from node.blockchain.types import AccountNumber

logger = logging.getLogger(__name__)

T = TypeVar('T', bound='NodeClient')

DEFAULT_TIMEOUT = 2
LIST_NODES_LIMIT = 20
LIST_BLOCKS_LIMIT = 20


def setdefault_if_not_none(dict_, key, value):
    if value is not None:
        dict_.setdefault(key, value)


def with_node(method_or_none=None, should_raise=False):

    def decorator(method):

        @functools.wraps(method)
        def wrapper(self, /, source: Union[str, Node], *args, **kwargs):
            if isinstance(source, str):
                return method(self, source, *args, **kwargs)

            assert isinstance(source, Node)

            for address in source.addresses:
                try:
                    rv = method(self, address, *args, **kwargs)
                except Exception:
                    exc_info = sys.exc_info()
                    rv = None
                else:
                    exc_info = None  # type: ignore

                if exc_info or rv is None:
                    logger.warning(
                        'Unsuccessful API call with %s(%r, ...)', method.__name__, str(address), exc_info=exc_info
                    )
                    continue

                return rv

            if should_raise:
                raise ConnectionError(f'Unsuccessful API call with {method.__name__}({source!r}, ...)')
            else:
                return None

        return wrapper

    return decorator(method_or_none) if method_or_none else decorator


def raise_for_status_advanced(response):
    try:
        response.raise_for_status()
    except requests.HTTPError as ex:
        args = ex.args
        if args:
            ex.args = (args[0] + f' (BODY: {response.text})',) + args[1:]
        else:
            ex.args = (f'Response BODY: {response.text}',)
        raise


class NodeClient:
    _instance = None

    def __init__(self):
        self.timeout = DEFAULT_TIMEOUT

    @classmethod
    def get_instance(cls: Type[T]) -> T:
        instance = cls._instance
        if not instance:
            instance = cls()
            cls.set_instance_cache(instance)

        return instance

    @classmethod
    def set_instance_cache(cls: Type[T], instance: T):
        cls._instance = instance

    @classmethod
    def clear_instance_cache(cls):
        cls._instance = None

    @staticmethod
    def requests_post(url, *args, **kwargs):  # We need this method for mocking in unittests
        return requests.post(url, *args, **kwargs)

    @staticmethod
    def requests_get(url, *args, **kwargs):  # We need this method for mocking in unittests
        return requests.get(url, *args, **kwargs)

    def http_post(self, address, resource, json_data=None, data=None, *, should_raise=True):
        url = urljoin(address, f'/api/{resource}/')

        try:
            response = self.requests_post(
                url, json=json_data, data=data, headers={'Content-Type': 'application/json'}, timeout=self.timeout
            )
        except Exception:
            logger.warning('Could not POST %s, data: %s', url, data if json_data is None else json_data, exc_info=True)
            if should_raise:
                raise

            return None

        if should_raise:
            raise_for_status_advanced(response)
        else:
            status_code = response.status_code
            if status_code >= 400:
                logger.warning(
                    'Could not POST %s: HTTP%s: %s, data: %s', url, status_code, response.text,
                    data if json_data is None else json_data
                )

        return response

    def http_get(self, address, resource, *, resource_id=None, parameters=None, should_raise=True):
        path = f'/api/{resource}/'
        if resource_id is not None:
            path += f'{resource_id}/'

        url = urljoin(address, path)
        if parameters:
            url += '?' + urlencode(parameters)

        try:
            response = self.requests_get(url, timeout=self.timeout)
        except Exception:
            logger.warning('Could not GET %s', url, exc_info=True)
            if should_raise:
                raise

            return None

        if should_raise:
            raise_for_status_advanced(response)
        else:
            status_code = response.status_code
            if status_code >= 400:
                logger.warning('Could not GET %s: HTTP%s: %s', url, status_code, response.text)
        return response

    def list_resource(
        self, address, resource, *, offset=None, limit=None, ordering=None, parameters=None, should_raise=True
    ):
        parameters = (parameters or {}).copy()
        setdefault_if_not_none(parameters, 'offset', offset)
        setdefault_if_not_none(parameters, 'limit', limit)
        setdefault_if_not_none(parameters, 'ordering', ordering)
        return self.http_get(address, resource, parameters=parameters, should_raise=should_raise)

    def yield_resource(self, address, resource, by_limit, parameters: Optional[dict] = None):
        offset = 0
        while True:
            response = self.list_resource(address, resource, offset=offset, limit=by_limit, parameters=parameters)
            if response is None:
                break

            items = response.json().get('results')
            if not items:
                break

            logger.debug('Got %s items', len(items))
            for item in items:
                yield item

            offset += len(items)

    @with_node
    def send_signed_change_request(self, /, address: str, signed_change_request: SignedChangeRequest):
        logger.debug('Sending %s to %s', signed_change_request, address)
        # TODO(dmu) LOW: Consider using `json=signed_change_request.dict()`, but this requires serialization
        #                enums to basic types in dict while still having enums in model instance representation
        return self.http_post(address, 'signed-change-requests', data=signed_change_request.json())

    @with_node
    def send_block(self, /, address: str, block: Union[Block, str]):
        logger.debug('Sending %s to %s', block, address)
        return self.http_post(address, 'blocks', data=block.json() if isinstance(block, Block) else block)

    @with_node
    def send_block_confirmation(self, /, address: str, block_confirmation: BlockConfirmation):
        logger.debug('Sending %s to %s', block_confirmation, address)
        return self.http_post(address, 'block-confirmations', data=block_confirmation.json())

    def yield_nodes(self, /, address: str) -> Generator[Node, None, None]:
        for item in self.yield_resource(address, 'nodes', by_limit=LIST_NODES_LIMIT):
            yield Node.parse_obj(item)

    @with_node
    def list_nodes(self, /, address: str) -> list[Node]:
        return list(self.yield_nodes(address))

    def get_node_online_address(self, node) -> Optional[str]:
        # TODO(dmu) MEDIUM: What should we do if node is not declared, but responds API calls?
        for address in node.addresses:
            try:
                self.http_get(address, 'nodes', resource_id='self')
            except Exception:
                logger.warning('Node %s is not online on %s', node, address, exc_info=True)
            else:
                return address

        return None

    @with_node
    def get_block_raw(self, /, address: str, block_number: Union[int, str]) -> Optional[str]:
        response = self.http_get(address, 'blocks', resource_id=block_number, should_raise=False)
        if response is None or response.status_code == 404:
            return None

        response.raise_for_status()
        return response.text

    @with_node
    def get_block(self, /, address: str, block_number: Union[int, str]) -> Optional[Block]:
        block = self.get_block_raw(address, block_number)
        if block is None:
            return None

        return Block.parse_raw(block)

    @with_node
    def get_last_block(self, /, address) -> Optional[Block]:
        return self.get_block(address, 'last')

    @with_node
    def get_last_block_number(self, /, address) -> Optional[int]:
        last_block = self.get_last_block(address)
        return last_block.get_block_number() if last_block else None

    def yield_blocks_dict(
        self,
        /,
        address: str,
        block_number_min: Optional[int] = None,
        block_number_max: Optional[int] = None,
        by_limit: Optional[int] = None,
    ) -> Generator[dict, None, None]:
        parameters: dict = {}
        setdefault_if_not_none(parameters, 'block_number_min', block_number_min)
        setdefault_if_not_none(parameters, 'block_number_max', block_number_max)

        by_limit = LIST_BLOCKS_LIMIT if by_limit is None else by_limit
        yield from self.yield_resource(address, 'blocks', by_limit=by_limit, parameters=parameters)

    @with_node
    def list_blocks_dict(self, /, address: str) -> list[dict]:
        return list(self.yield_blocks_dict(address))

    @with_node
    def get_account_state(self, /, address: str, account_number: AccountNumber) -> AccountState:
        response = self.http_get(address, 'account-states', resource_id=account_number)
        return AccountState.parse_raw(response.text)
