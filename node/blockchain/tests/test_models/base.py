import pytest

VALID = object()
CREATE = object()

account_lock_tests = (  # type: ignore
    (None, r'account_lock.*none is not an allowed value', {'message.account_lock': ['none is not an allowed value']}),
    ('', r'account_lock.*ensure this value has at least 64 characters', {
        'message.account_lock': ['ensure this value has at least 64 characters']}),
    ('a', r'account_lock.*ensure this value has at least 64 characters', {
        'message.account_lock': ['ensure this value has at least 64 characters']}),
    (
        '1c8e5f54a15b63a9f3d540ce505fd0799575ffeaac62ce625c917e6d915ea8bbd',
        r'account_lock.*ensure this value has at most 64 characters', {
            'message.account_lock': ['ensure this value has at most 64 characters']}
    ),
    (
        '@c8e5f54a15b63a9f3d540ce505fd0799575ffeaac62ce625c917e6d915ea8bb',  # non-hex characters
        r'account_lock.*string does not match regex', {
            'message.account_lock': ['string does not match regex "^[0-9a-f]+$"']}
    ),
    ({}, r'account_lock.*str type expected', {'message.account_lock': ['str type expected']}),
)

node_tests = (
    (None, r'node.*none is not an allowed value', {
        'message.node': ['none is not an allowed value']
    }),
    ('invalid-type', r'node.*value is not a valid dict', {
        'message.node': ['value is not a valid dict']
    }),
)

node_identifier_tests = (  # type: ignore
    (None, r'identifier.*none is not an allowed value'),
    ('', r'identifier.*ensure this value has at least 64 characters'),
    ('a', r'identifier.*ensure this value has at least 64 characters'),
    (
        '1c8e5f54a15b63a9f3d540ce505fd0799575ffeaac62ce625c917e6d915ea8bbd',
        r'identifier.*ensure this value has at most 64 characters'
    ),
    ('@c8e5f54a15b63a9f3d540ce505fd0799575ffeaac62ce625c917e6d915ea8bb', r'identifier.*string does not match regex'),
    ({}, r'identifier.*str type expected'),
)

node_addresses_tests = (
    (None, r'addresses.*none is not an allowed value', {
        'message.node.addresses': ['none is not an allowed value']
    }),
    ('', r'addresses.*value is not a valid list', {
        'message.node.addresses': ['value is not a valid list']
    }),
    (
        'http://not-existing-node-address-674898923.com:8555/', r'addresses.*value is not a valid list', {
            'message.node.addresses': ['value is not a valid list']
        }
    ),
    # TODO(dmu) HIGH: Support node unregistering and move out the case we empty `addresses`
    #                 https://thenewboston.atlassian.net/browse/BC-161
    # TODO(dmu) HIGH: Implement non-empty list validation
    #                 https://thenewboston.atlassian.net/browse/BC-161
    # ([], r'not-implemented'),
    (['not-an-url'], r'addresses.*invalid or missing URL scheme', {
        'message.node.addresses.0': ['invalid or missing URL scheme']
    }),
)

node_fee_tests = (
    (None, r'fee.*none is not an allowed value', {
        'message.node.fee': ['none is not an allowed value']
    }),
    (
        -1, r'fee.*ensure this value is greater than or equal to 0', {
            'message.node.fee': ['ensure this value is greater than or equal to 0']
        }
    ),
    (1.2, r'fee.*value is not a valid integer', {
        'message.node.fee': ['value is not a valid integer']
    }),
    ('str', r'fee.*value is not a valid integer', {
        'message.node.fee': ['value is not a valid integer']
    }),
    ('1', r'fee.*value is not a valid integer', {
        'message.node.fee': ['value is not a valid integer']
    }),
)

node_declaration_message_type_validation_parametrizer = pytest.mark.parametrize(
    # keep `id_` to make debugging easier
    'id_, account_lock, node, node_identifier, node_addresses, node_fee, search_re',
    tuple((1, item[0], VALID, None, None, None, item[1]) for item in account_lock_tests) +
    tuple((2, VALID, item[0], None, None, None, item[1]) for item in node_tests) +
    tuple((3, VALID, CREATE, item[0], VALID, VALID, item[1]) for item in node_identifier_tests) +
    tuple((4, VALID, CREATE, VALID, item[0], VALID, item[1]) for item in node_addresses_tests) +
    tuple((5, VALID, CREATE, VALID, VALID, item[0], item[1]) for item in node_fee_tests)
)

node_declaration_message_type_api_validation_parametrizer = pytest.mark.parametrize(
    # keep `id_` to make debugging easier
    'id_, account_lock, node, node_addresses, node_fee, expected_response_body',
    tuple((1, item[0], VALID, None, None, item[2]) for item in account_lock_tests) +
    tuple((2, VALID, item[0], None, None, item[2]) for item in node_tests) +
    tuple((4, VALID, CREATE, item[0], VALID, item[2]) for item in node_addresses_tests) +
    tuple((5, VALID, CREATE, VALID, item[0], item[2]) for item in node_fee_tests)
)
