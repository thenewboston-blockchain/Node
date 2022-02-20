import pytest

from node.blockchain.types import Type


@pytest.mark.django_db
@pytest.mark.parametrize('type_', (Type.GENESIS, Type.PV_SCHEDULE_UPDATE))
def test_unsupported_types(
    type_, smart_mocked_node_client, test_server_address, genesis_signed_change_request,
    pv_schedule_update_signed_change_request
):
    requests = {
        Type.GENESIS: genesis_signed_change_request,
        Type.PV_SCHEDULE_UPDATE: pv_schedule_update_signed_change_request,
    }
    signed_change_request = requests[type_]
    response = smart_mocked_node_client.http_post(
        test_server_address, 'signed-change-requests', data=signed_change_request.json(), should_raise=False
    )
    assert response.status_code == 400
    assert response.json() == {'message.type': [{'message': 'Invalid value.', 'code': 'invalid'}]}
