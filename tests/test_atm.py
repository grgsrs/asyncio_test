import pytest

import customer_pb2


@pytest.mark.asyncio
async def test_jane_withdraw(event_loop, bank_server, atm_process, client):
    success, balance = await client.send_request(
        "Jane Doe", customer_pb2.WITHDRAW, 100
    )
    assert success
    assert balance == 0


@pytest.mark.asyncio
async def test_john_withdraw(event_loop, bank_server, atm_process, client):
    success, balance = await client.send_request(
        "John Doe", customer_pb2.WITHDRAW, 100
    )
    assert success
    assert balance == 400.0


@pytest.mark.asyncio
async def test_anon_withdraw(event_loop, bank_server, atm_process, client):
    success, balance = await client.send_request(
        "Anonymous", customer_pb2.WITHDRAW, 100
    )
    assert not success
    assert balance == 0
