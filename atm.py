import asyncio
from struct import pack, unpack_from

import bank_pb2
import customer_pb2


class BankClientProtocol(asyncio.Protocol):
    def __init__(self, loop):
        self.loop = loop
        self.transport = None
        self.futures = dict()

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        length = unpack_from("!H", data)[0]
        response = bank_pb2.Response.FromString(data[2:length + 2])
        future = self.futures.pop(response.customer_id)
        future.set_result(response.balance)

    def get_balance(self, customer_id):
        future = self.loop.create_future()
        self.futures[customer_id] = future
        req = bank_pb2.GetBalance(customer_id=customer_id)
        msg = pack("!H", req.ByteSize()) + req.SerializeToString()
        self.transport.write(msg)
        return future


class AtmServerProtocol(asyncio.Protocol):
    def __init__(self, controller):
        self.controller = controller
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        length = unpack_from("!H", data)[0]
        request = customer_pb2.Request.FromString(data[2:length + 2])
        coro = self.controller.on_customer_request(self, request)
        asyncio.ensure_future(coro)

    def send_balance(self, success, balance):
        reply = customer_pb2.Reply(success=success, balance=balance)
        msg = pack("!H", reply.ByteSize()) + reply.SerializeToString()
        self.transport.write(msg)
        self.transport.close()


class Controller(object):
    def __init__(self, loop):
        self.loop = loop
        self.client = None
        self.server = None

    async def startup(self):
        _, self.client = await self.loop.create_connection(
            lambda: BankClientProtocol(self.loop), port=44444
        )
        self.server = await self.loop.create_server(
            lambda: AtmServerProtocol(controller), port=33333
        )

    async def on_customer_request(self, protocol, request):
        balance = await self.client.get_balance(request.customer_id)
        if request.request_type == customer_pb2.DEPOSIT:
            success = True
            balance += request.amount
        else:
            success = request.amount <= balance
            if success:
                balance -= request.amount
        protocol.send_balance(success, balance)


loop = asyncio.get_event_loop()
controller = Controller(loop)
loop.run_until_complete(controller.startup())
loop.run_forever()
