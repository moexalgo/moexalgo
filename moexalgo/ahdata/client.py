import asyncio
import typing as t
from time import sleep

import httpx

from moexalgo.session import BaseClient
from moexalgo.utils import json


class Client(BaseClient):
    """
    Клиент для работы с API AlgopackHistorical Data
    """

    def get(self, path: str, **params: t.Any) -> t.Any:

        def _parse_response(resp: httpx.Response) -> t.Any:
            if resp.url.raw_path == b'/error?message=Authentication+required+to+download+files':
                resp = httpx.Response(401, request=resp.request)
            if not resp.is_success:
                resp.raise_for_status()
            if resp.headers['content-type'].startswith('application/json'):
                if data := json.loads(resp.text):
                    return data
            return resp.content

        def _sync_get(timeout: float = 0):
            if timeout:
                sleep(timeout)
            return _parse_response(self.httpx_cli.get(path, params=params))

        async def _async_get(timeout: float = 0):
            if timeout:
                await asyncio.sleep(timeout)
            return _parse_response(await self.httpx_cli.get(path, params=params))

        return _sync_get() if self.sync else _async_get()
