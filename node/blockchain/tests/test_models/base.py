import pytest

VALID = object()
CREATE = object()

node_declaration_message_type_validation_parametrizer = pytest.mark.parametrize(
    # keep `id_` to make debugging easier
    'id_, account_lock, node, node_identifier, node_addresses, node_fee, search_re',
    (
        # account_lock
        (1, None, VALID, None, None, None, r'account_lock.*none is not an allowed value'),
        (2, '', VALID, None, None, None, r'account_lock.*ensure this value has at least 64 characters'),
        (3, 'a', VALID, None, None, None, r'account_lock.*ensure this value has at least 64 characters'),
        (
            4, '1c8e5f54a15b63a9f3d540ce505fd0799575ffeaac62ce625c917e6d915ea8bbd', VALID, None, None, None,
            r'account_lock.*ensure this value has at most 64 characters'
        ),
        (
            5,
            '@c8e5f54a15b63a9f3d540ce505fd0799575ffeaac62ce625c917e6d915ea8bb',  # non-hex characters
            VALID,
            None,
            None,
            None,
            r'account_lock.*string does not match regex'
        ),
        (6, {}, VALID, None, None, None, r'account_lock.*str type expected'),

        # node
        (7, VALID, None, None, None, None, r'node.*none is not an allowed value'),
        (8, VALID, 'invalid-type', None, None, None, r'node.*value is not a valid dict'),

        # node.identifier
        (9, VALID, CREATE, None, VALID, VALID, r'identifier.*none is not an allowed value'),
        (10, VALID, CREATE, '', VALID, VALID, r'identifier.*ensure this value has at least 64 characters'),
        (11, VALID, CREATE, 'a', VALID, VALID, r'identifier.*ensure this value has at least 64 characters'),
        (
            12, VALID, CREATE, '1c8e5f54a15b63a9f3d540ce505fd0799575ffeaac62ce625c917e6d915ea8bbd', VALID, VALID,
            r'identifier.*ensure this value has at most 64 characters'
        ),
        (
            13, VALID, CREATE, '@c8e5f54a15b63a9f3d540ce505fd0799575ffeaac62ce625c917e6d915ea8bb', VALID, VALID,
            r'identifier.*string does not match regex'
        ),
        (14, VALID, CREATE, {}, VALID, VALID, r'identifier.*str type expected'),

        # node.addresses
        (15, VALID, CREATE, VALID, None, VALID, r'addresses.*none is not an allowed value'),
        (16, VALID, CREATE, VALID, '', VALID, r'addresses.*value is not a valid list'),
        (
            17, VALID, CREATE, VALID, 'http://not-existing-node-address-674898923.com:8555/', VALID,
            r'addresses.*value is not a valid list'
        ),
        # TODO(dmu) HIGH: Support node unregistering and move out the case we empty `addresses`
        #                 https://thenewboston.atlassian.net/browse/BC-161
        # TODO(dmu) HIGH: Implement non-empty list validation
        #                 https://thenewboston.atlassian.net/browse/BC-161
        # (18, VALID, CREATE, VALID, [], VALID, r'not-implemented'),
        (19, VALID, CREATE, VALID, ['not-an-url'], VALID, r'addresses.*invalid or missing URL scheme'),

        # node.fee
        (20, VALID, CREATE, VALID, VALID, None, r'fee.*none is not an allowed value'),
        (21, VALID, CREATE, VALID, VALID, -1, r'fee.*ensure this value is greater than or equal to 0'),
        (22, VALID, CREATE, VALID, VALID, 1.2, r'fee.*value is not a valid integer'),
        (23, VALID, CREATE, VALID, VALID, 'str', r'fee.*value is not a valid integer'),
        (24, VALID, CREATE, VALID, VALID, '1', r'fee.*value is not a valid integer'),
    )
)
