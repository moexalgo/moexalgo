import asyncio
import json
import typing as t
import uuid
from collections import deque
from contextlib import asynccontextmanager

import websockets
from stomp.utils import Frame, convert_frame, parse_frame


class Credentials(t.NamedTuple):
    """ Auth credentials """
    domain: str
    login: str
    passcode: str


class Subscription(t.AsyncIterator):

    def __init__(self, id: str):
        self.id = id
        self._queue = deque(maxlen=256)

    def _append(self, data):
        self._queue.append(data)

    async def __anext__(self):
        while not len(self._queue):
            await asyncio.sleep(0.1)
        result = self._queue.popleft()
        if isinstance(result, Exception):
            raise result
        return result


class ISSPlusSTOMP:
    """ ISS+ STOMP Client """

    structure: dict[str, t.Any] = dict()

    def __init__(self, wscp: websockets.WebSocketClientProtocol, cred: Credentials):
        self._wscp = wscp
        self._cred = cred
        self._task = None  # type: asyncio.Task | None
        self._pending = dict()  # type: dict[str, asyncio.Future | Subscription]

    def __await__(self):
        return self.run_forever().__await__()

    async def __aenter__(self):
        auth_frame = Frame('CONNECT', headers=self._cred._asdict())
        await self._wscp.send(b''.join(convert_frame(auth_frame)))
        async for message in self._wscp:
            frame = parse_frame(message)
            if frame.cmd == 'CONNECTED':
                self.structure = json.loads(frame.body.decode('utf8').strip('\0'))['structure']
                self._task = asyncio.create_task(self._listener(), name="Message listener")
                return self
            raise ConnectionRefusedError(f"STOMP authentication failed; {frame.headers['message']}")

    async def __aexit__(self, *exc_info):
        if self._task:
            if not self._task.done():
                self._task.cancel()
        self._task = None

    async def request(self, destination, selector):
        id = str(uuid.uuid4())
        req_frame = Frame('REQUEST', headers=dict(id=id, destination=destination, selector=selector))
        await self._wscp.send(b''.join(convert_frame(req_frame)))
        future = self._pending[id] = asyncio.Future()
        return await future

    async def subscribe(self, destination, selector):
        id = str(uuid.uuid4())
        subs_frame = Frame('SUBSCRIBE', headers=dict(id=id, receipt=id, destination=destination, selector=selector))
        await self._wscp.send(b''.join(convert_frame(subs_frame)))
        subscription = self._pending[id] = Subscription(id)
        return subscription

    async def unsubscribe(self, id: str):
        unsub_frame = Frame('UNSUBSCRIBE', headers=dict(id=id))
        await self._wscp.send(b''.join(convert_frame(unsub_frame)))
        subscription = self._pending.pop(id, None)
        subscription._append(StopAsyncIteration())

    async def run_forever(self):
        if self._task is None:
            raise ConnectionError("Client is not connected")
        await self._task

    async def close(self):
        if self._wscp is None:
            raise ConnectionError("Client is not connected")
        while self._pending:
            item = self._pending[tuple(self._pending.keys())[0]]
            if isinstance(item, Subscription):
                await self.unsubscribe(item.id)
            elif isinstance(item, asyncio.Future):
                item.cancel()
            else:
                assert False
        await self._wscp.close()

    async def _listener(self):
        try:
            async for message in self._wscp:
                frame = parse_frame(message)
                if request_id := frame.headers.get('request-id'):
                    if future := self._pending.pop(request_id, None):
                        if frame.cmd == 'ERROR':
                            future.set_exception(
                                RuntimeError(f"Request {request_id} failed: {frame.headers['message']}"))
                        else:
                            future.set_result(json.loads(frame.body.decode('utf8').strip('\0')))
                    else:
                        assert False, f"Cannot found pending for request: {request_id}"
                elif subscription_id := frame.headers.get('subscription', frame.headers.get('receipt-id')):
                    if subscription := self._pending.get(subscription_id, None):
                        if frame.cmd == 'ERROR':
                            subscription._append(
                                RuntimeError(f"Subscription {subscription_id} failed: {frame.headers['message']}"))
                            self._pending.pop(subscription_id, None)
                        else:
                            data = frame.body.decode('utf8').strip('\0')
                            if data:
                                subscription._append(json.loads(data))
                    else:
                        assert False, f"Cannot found pending for subscription: {subscription_id}"
                else:
                    assert False
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            print(exc)


@asynccontextmanager
async def connect(url: str, credentials: Credentials):
    async with websockets.connect(url, subprotocols=['STOMP']) as websocket:
        async with ISSPlusSTOMP(websocket, credentials) as iss_plus:
            yield iss_plus
