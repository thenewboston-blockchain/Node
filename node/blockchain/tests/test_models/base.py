import pytest

VALID = object()
CREATE = object()

account_lock_tests = (  # type: ignore
    (None, r'account_lock.*none is not an allowed value',
     {'message.account_lock': [{'code': 'invalid', 'message': 'none is not an allowed value'}]}),
    ('', r'account_lock.*ensure this value has at least 64 characters', {
        'message.account_lock': [{'code': 'invalid', 'message': 'ensure this value has at least 64 characters'}]}),
    ('a', r'account_lock.*ensure this value has at least 64 characters', {
        'message.account_lock': [{'code': 'invalid', 'message': 'ensure this value has at least 64 characters'}]}),
    (
        '1c8e5f54a15b63a9f3d540ce505fd0799575ffeaac62ce625c917e6d915ea8bbd',
        r'account_lock.*ensure this value has at most 64 characters', {
            'message.account_lock': [{'code': 'invalid', 'message': 'ensure this value has at most 64 characters'}]}
    ),
    (
        '@c8e5f54a15b63a9f3d540ce505fd0799575ffeaac62ce625c917e6d915ea8bb',  # non-hex characters
        r'account_lock.*string does not match regex', {
            'message.account_lock': [{'code': 'invalid', 'message': 'string does not match regex "^[0-9a-f]+$"'}]}
    ),
    ({}, r'account_lock.*str type expected',
     {'message.account_lock': [{'code': 'invalid', 'message': 'str type expected'}]}),
)

node_tests = (
    (
        None, r'node.*none is not an allowed value', {
            'message.node': [{
                'code': 'invalid',
                'message': 'none is not an allowed value'
            }]
        }
    ),
    (
        'invalid-type', r'node.*value is not a valid dict', {
            'message.node': [{
                'code': 'invalid',
                'message': 'value is not a valid dict'
            }]
        }
    ),
)

node_identifier_tests = (  # type: ignore
    (
        None,
        r'identifier.*none is not an allowed value',
        r'schedule -> 1.*none is not an allowed value'
    ),
    (
        '',
        r'identifier.*ensure this value has at least 64 characters',
        r'schedule -> 1.*ensure this value has at least 64 characters'
    ),
    (
        'a',
        r'identifier.*ensure this value has at least 64 characters',
        r'schedule -> 1.*ensure this value has at least 64 characters'
    ),
    (
        '1c8e5f54a15b63a9f3d540ce505fd0799575ffeaac62ce625c917e6d915ea8bbd',
        r'identifier.*ensure this value has at most 64 characters',
        r'schedule -> 1.*ensure this value has at most 64 characters'
    ),
    (
        '@c8e5f54a15b63a9f3d540ce505fd0799575ffeaac62ce625c917e6d915ea8bb',
        r'identifier.*string does not match regex',
        r'schedule -> 1.*string does not match regex'),
    (
        {},
        r'identifier.*str type expected',
        r'schedule -> 1.*str type expected'
    ),
)

node_addresses_tests = (
    (
        None, r'addresses.*none is not an allowed value', {
            'message.node.addresses': [{
                'code': 'invalid',
                'message': 'none is not an allowed value'
            }]
        }
    ),
    (
        '', r'addresses.*value is not a valid list', {
            'message.node.addresses': [{
                'code': 'invalid',
                'message': 'value is not a valid list'
            }]
        }
    ),
    (
        'http://not-existing-node-address-674898923.com:8555/', r'addresses.*value is not a valid list', {
            'message.node.addresses': [{
                'code': 'invalid',
                'message': 'value is not a valid list'
            }]
        }
    ),
    # TODO(dmu) HIGH: Support node unregistering and move out the case we empty `addresses`
    #                 https://thenewboston.atlassian.net/browse/BC-161
    # TODO(dmu) HIGH: Implement non-empty list validation
    #                 https://thenewboston.atlassian.net/browse/BC-161
    # ([], r'not-implemented'),
    (['not-an-url'], r'addresses.*invalid or missing URL scheme', {
        'message.node.addresses.0': [{
            'code': 'invalid',
            'message': 'invalid or missing URL scheme'
        }]
    }),
)

node_fee_tests = (
    (
        None, r'fee.*none is not an allowed value', {
            'message.node.fee': [{
                'code': 'invalid',
                'message': 'none is not an allowed value'
            }]
        }
    ),
    (
        -1, r'fee.*ensure this value is greater than or equal to 0', {
            'message.node.fee': [{
                'code': 'invalid',
                'message': 'ensure this value is greater than or equal to 0'
            }]
        }
    ),
    (
        1.2, r'fee.*value is not a valid integer', {
            'message.node.fee': [{
                'code': 'invalid',
                'message': 'value is not a valid integer'
            }]
        }
    ),
    (
        'str', r'fee.*value is not a valid integer', {
            'message.node.fee': [{
                'code': 'invalid',
                'message': 'value is not a valid integer'
            }]
        }
    ),
    (
        '1', r'fee.*value is not a valid integer', {
            'message.node.fee': [{
                'code': 'invalid',
                'message': 'value is not a valid integer'
            }]
        }
    ),
)

transaction_tests = (
    (
        None, r'txs -> 0.*none is not an allowed value', {
            'message.txs.0': [{
                'code': 'invalid',
                'message': 'none is not an allowed value'
            }]
        }
    ),
    (
        'invalid-type', r'txs -> 0.*value is not a valid dict', {
            'message.txs.0': [{
                'code': 'invalid',
                'message': 'value is not a valid dict'
            }]
        }
    ),
)

recipient_tests = (
    (
        None, r'recipient.*none is not an allowed value', {
            'message.txs.0.recipient': [{
                'code': 'invalid',
                'message': 'none is not an allowed value'
            }]
        }
    ),
    (
        '', r'recipient.*ensure this value has at least 64 characters', {
            'message.txs.0.recipient': [{
                'code': 'invalid',
                'message': 'ensure this value has at least 64 characters'
            }]
        }
    ),
    (
        'not-a-recipient-address', r'recipient.*ensure this value has at least 64 characters', {
            'message.txs.0.recipient': [{
                'code': 'invalid',
                'message': 'ensure this value has at least 64 characters'
            }]
        }
    ),
    (
        123, r'recipient.*str type expected', {
            'message.txs.0.recipient': [{
                'code': 'invalid',
                'message': 'str type expected'
            }]
        }
    ),
)

is_fee_tests = (
    (
        '', r'is_fee.*value is not a valid boolean', {
            'message.txs.0.is_fee': [{
                'code': 'invalid',
                'message': 'value is not a valid boolean'
            }]
        }
    ),
    (
        'not-a-boolean', r'is_fee.*value is not a valid boolean', {
            'message.txs.0.is_fee': [{
                'code': 'invalid',
                'message': 'value is not a valid boolean'
            }]
        }
    ),
    (
        1, r'is_fee.*value is not a valid boolean', {
            'message.txs.0.is_fee': [{
                'code': 'invalid',
                'message': 'value is not a valid boolean'
            }]
        }
    ),
    (
        'True', r'is_fee.*value is not a valid boolean', {
            'message.txs.0.is_fee': [{
                'code': 'invalid',
                'message': 'value is not a valid boolean'
            }]
        }
    ),
)

amount_tests = (
    (
        None, r'amount.*none is not an allowed value', {
            'message.txs.0.amount': [{
                'code': 'invalid',
                'message': 'none is not an allowed value'
            }]
        }
    ),
    (
        '', r'amount.*value is not a valid integer', {
            'message.txs.0.amount': [{
                'code': 'invalid',
                'message': 'value is not a valid integer'
            }]
        }
    ),
    (
        'not-a-number', r'amount.*value is not a valid integer', {
            'message.txs.0.amount': [{
                'code': 'invalid',
                'message': 'value is not a valid integer'
            }]
        }
    ),
    (
        '10', r'amount.*value is not a valid integer', {
            'message.txs.0.amount': [{
                'code': 'invalid',
                'message': 'value is not a valid integer'
            }]
        }
    ),
    (
        -5, r'amount.*ensure this value is greater than 0', {
            'message.txs.0.amount': [{
                'code': 'invalid',
                'message': 'ensure this value is greater than 0'
            }]
        }
    ),
    (
        0, r'amount.*ensure this value is greater than 0', {
            'message.txs.0.amount': [{
                'code': 'invalid',
                'message': 'ensure this value is greater than 0'
            }]
        }
    ),
)

memo_tests = (
    (56, r'memo.*str type expected', {
        'message.txs.0.memo': [{
            'code': 'invalid',
            'message': 'str type expected'
        }]
    }),
    (True, r'memo.*str type expected', {
        'message.txs.0.memo': [{
            'code': 'invalid',
            'message': 'str type expected'
        }]
    }),
)

schedule_block_number_on_instantiation_tests = (
    (
        None, r'schedule -> __key__.*none is not an allowed value', {
            'message.txs.0.amount': [{
                'code': 'invalid',
                'message': 'none is not an allowed value'
            }]
        }
    ),
    (
        '', r'schedule -> __key__.*string does not match regex "\^\(\?\:0\|\[1-9\]\[0-9\]\*\)\$"', {
            'message.txs.0.amount': [{
                'code': 'invalid',
                'message': 'value is not a valid integer'
            }]
        }
    ),
    (
        'not-a-number', r'schedule -> __key__.*string does not match regex "\^\(\?\:0\|\[1-9\]\[0-9\]\*\)\$"', {
            'message.txs.0.amount': [{
                'code': 'invalid',
                'message': 'value is not a valid integer'
            }]
        }
    ),
    (
        10, r'schedule -> __key__.*str type expected', {
            'message.txs.0.amount': [{
                'code': 'invalid',
                'message': 'value is not a valid integer'
            }]
        }
    ),
    (
        -5, r'schedule -> __key__.*str type expected', {
            'message.txs.0.amount': [{
                'code': 'invalid',
                'message': 'ensure this value is greater than 0'
            }]
        }
    ),
    (
        '-3', r'schedule -> __key__.*string does not match regex "\^\(\?\:0\|\[1-9\]\[0-9\]\*\)\$"', {
            'message.txs.0.amount': [{
                'code': 'invalid',
                'message': 'ensure this value is greater than 0'
            }]
        }
    ),
)

schedule_block_number_on_parsing_tests = (
    (
        None, r'schedule -> __key__.*string does not match regex "\^\(\?\:0\|\[1-9\]\[0-9\]\*\)\$"', {
            'message.txs.0.amount': [{
                'code': 'invalid',
                'message': 'none is not an allowed value'
            }]
        }
    ),
    (
        '', r'schedule -> __key__.*string does not match regex "\^\(\?\:0\|\[1-9\]\[0-9\]\*\)\$"', {
            'message.txs.0.amount': [{
                'code': 'invalid',
                'message': 'value is not a valid integer'
            }]
        }
    ),
    (
        'not-a-number', r'schedule -> __key__.*string does not match regex "\^\(\?\:0\|\[1-9\]\[0-9\]\*\)\$"', {
            'message.txs.0.amount': [{
                'code': 'invalid',
                'message': 'value is not a valid integer'
            }]
        }
    ),
    (
        -5, r'schedule -> __key__.*string does not match regex "\^\(\?\:0\|\[1-9\]\[0-9\]\*\)\$"', {
            'message.txs.0.amount': [{
                'code': 'invalid',
                'message': 'ensure this value is greater than 0'
            }]
        }
    ),
    (
        '-3', r'schedule -> __key__.*string does not match regex "\^\(\?\:0\|\[1-9\]\[0-9\]\*\)\$"', {
            'message.txs.0.amount': [{
                'code': 'invalid',
                'message': 'ensure this value is greater than 0'
            }]
        }
    ),
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
    tuple((3, VALID, CREATE, item[0], VALID, item[2]) for item in node_addresses_tests) +
    tuple((4, VALID, CREATE, VALID, item[0], item[2]) for item in node_fee_tests)
)

coin_transfer_message_type_validation_parametrizer = pytest.mark.parametrize(
    # keep `id_` to make debugging easier
    'id_, account_lock, transaction, recipient, is_fee, amount, memo, search_re, expected_response_body',
    tuple((1, item[0], VALID, None, None, None, None, item[1], item[2]) for item in account_lock_tests) +
    tuple((2, VALID, item[0], None, None, None, None, item[1], item[2]) for item in transaction_tests) +
    tuple((3, VALID, CREATE, item[0], VALID, VALID, VALID, item[1], item[2]) for item in recipient_tests) +
    tuple((4, VALID, CREATE, VALID, item[0], VALID, VALID, item[1], item[2]) for item in is_fee_tests) +
    tuple((5, VALID, CREATE, VALID, VALID, item[0], VALID, item[1], item[2]) for item in amount_tests) +
    tuple((6, VALID, CREATE, VALID, VALID, VALID, item[0], item[1], item[2]) for item in memo_tests)
)

pv_schedule_update_message_type_validation_on_instantiation_parametrizer = pytest.mark.parametrize(
    # keep `id_` to make debugging easier
    'id_, account_lock, schedule_block_number, node_identifier, search_re, expected_response_body',
    tuple((1, item[0], VALID, VALID, item[1], item[2]) for item in account_lock_tests) +
    tuple((2, VALID, item[0], VALID, item[1], item[2]) for item in schedule_block_number_on_instantiation_tests) +
    tuple((3, VALID, VALID, item[0], item[2], item[2]) for item in node_identifier_tests)
)

pv_schedule_update_message_type_validation_on_parsing_parametrizer = pytest.mark.parametrize(
    # keep `id_` to make debugging easier
    'id_, account_lock, schedule_block_number, node_identifier, search_re',
    tuple((1, item[0], VALID, VALID, item[1]) for item in account_lock_tests) +
    tuple((2, VALID, item[0], VALID, item[1]) for item in schedule_block_number_on_parsing_tests) +
    tuple((3, VALID, VALID, item[0], item[2]) for item in node_identifier_tests)
)
