import asyncio
import sys

from struct import pack, unpack_from

import pytest

import bank_pb2
import customer_pb2


def extract_message(data):
    length = unpack_from("!H", data)[0]
    return data[2:length + 2]


def pack_message(message):
    return pack("!H", message.ByteSize()) + message.SerializeToString()


class AtmClientProtocol(asyncio.Protocol):
    def __init__(self, loop):
        self.loop = loop
        self.future = None
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        reply = customer_pb2.Reply.FromString(extract_message(data))
        self.future.set_result((reply.success, reply.balance))

    def send_request(self, customer_id, request_type, amount):
        request = customer_pb2.Request()
        request.customer_id = customer_id
        request.request_type = request_type
        request.amount = amount
        self.transport.write(pack_message(request))

        self.future = self.loop.create_future()
        return self.future


BALANCES = {
    "Jane Doe": 100,
    "John Doe": 500
}


class BankServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        request = bank_pb2.GetBalance.FromString(extract_message(data))
        reply = bank_pb2.Response()
        reply.customer_id = request.customer_id
        reply.balance = BALANCES.get(request.customer_id, 0)
        self.transport.write(pack_message(reply))


@pytest.fixture
async def bank_server(event_loop):
    server = await event_loop.create_server(BankServerProtocol, port=44444)
    yield server
    server.close()


@pytest.fixture
async def atm_process(event_loop):
    process = await asyncio.create_subprocess_exec(
        sys.executable, b"../atm.py", loop=event_loop
    )
    await asyncio.sleep(0.5)
    yield process
    process.terminate()
    await process.wait()


@pytest.fixture
async def client(event_loop):
    _, client = await event_loop.create_connection(
        lambda: AtmClientProtocol(event_loop), port=33333
    )
    yield client
