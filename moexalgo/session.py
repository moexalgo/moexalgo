from __future__ import annotations

import asyncio
import typing as t
from time import time, sleep

import httpx

from moexalgo.utils import json, result_deserializer

BASE_URL = 'https://iss.moex.com/iss'
AUTH_URL = 'https://passport.moex.com/authenticate'
AUTH_CERT = None
USE_HTTPS = True
_NEXT_REQUEST_AT = 0
_REQUEST_TIMEOUT = 0.1


class HasOptions:

    def __init__(self, auth_cert: str = None, base_url=None, timeout=300, **options):
        base_url = base_url or BASE_URL
        if base_url.startswith('http:') and USE_HTTPS:
            base_url = base_url.replace('http:', 'https:')
        elif base_url.startswith('https:') and not USE_HTTPS:
            base_url = base_url.replace('https:', 'http:')
        self.__options = dict(**options, base_url=base_url, timeout=timeout)
        if auth_cert:
            self.__options.setdefault('cookies', {})['MicexPassportCert'] = auth_cert

    @property
    def options(self):
        """Опционные параметры использованные при создании сессии/клиента. """
        return self.__options


class Client(HasOptions):
    """API клиент """

    def __init__(self, sync: bool = True, **options):
        options['follow_redirects'] = True
        super().__init__(**options)
        self.httpx_cli = httpx.Client(**self.options) if sync else httpx.AsyncClient(**self.options)

    @property
    def sync(self):
        """Возвращает истину если клиент инициализирован для синхронного режима работы. """
        return isinstance(self.httpx_cli, httpx.Client)

    @property
    def authorized(self):
        """Осуществляет проверку авторизован клиент или нет

        Returns
        -------
        bool
            True если клиент авторизован, иначе False
        """

        return bool(self.options.get('auth_cert'))

    def authorize(self, username: str, password: str) -> str | None | t.Coroutine[t.Any, t.Any, str | None]:
        """ Метод для авторизации клиента

        Parameters
        ----------
        username: str
            Имя пользователя
        password: str
            Пароль
        Returns
        -------
        str
            Если
        None
            Если
        t.Coroutine[t.Any, t.Any, str | None]
            Если
        """

        def _process_response(resp: httpx.Response):
            if resp.is_success:
                return resp.cookies.get('MicexPassportCert', self.options.get('cookies', {}).get('MicexPassportCert'))
            return None

        async def _async_authorize():
            return _process_response(await self.httpx_cli.get(AUTH_URL, auth=(username, password)))

        def _sync_authorize():
            return _process_response(self.httpx_cli.get(AUTH_URL, auth=(username, password)))

        self.options['auth_cert'] = _sync_authorize() if self.sync else _async_authorize()
        return self.options['auth_cert']

    def get_objects(self, path: str, deserializer: t.Callable[[dict], dict | list], **params):
        """Реализует API запрос

        Parameters
        ----------
        path: str
        source: str
        deserializer: Callable[[dict], dict | list]
        params

        Returns
        -------

        Raises
        ------
        ValueError
            Если не удалось осуществить десериализацию данных
        """
        global _NEXT_REQUEST_AT
        path = [item for item in path.split('/') if item.strip()]
        url = '/'.join(path) + '.json'

        def _parse_response(resp: httpx.Response):
            if not resp.is_success:
                resp.raise_for_status()
            if not resp.headers['content-type'].startswith('application/json'):
                resp.status_code = 403
                resp.raise_for_status()
            if data := json.loads(resp.text):
                return deserializer(data)
            raise ValueError('Received wrong data')

        async def _async_get_objects(timeout):
            if timeout:
                await asyncio.sleep(timeout)
            return _parse_response(await self.httpx_cli.get(url, params=params))

        def _sync_get_objects(timeout):
            if timeout:
                sleep(timeout)
            return _parse_response(self.httpx_cli.get(url, params=params))

        timeout = _NEXT_REQUEST_AT - time()
        if self.authorized or timeout <= 0:
            timeout = 0.2
        _NEXT_REQUEST_AT = time() + _REQUEST_TIMEOUT + timeout

        return _sync_get_objects(timeout) if self.sync else _async_get_objects(timeout)

    @staticmethod
    def format_error(exc: httpx.HTTPStatusError):
        """Возвращает сообщение об ошибке

        Parameters
        ----------
        exc: httpx.HTTPStatusError

        Returns
        -------
        str
            Сообщение об ошибке
        """
        return (
            f"HTTP request to {str(exc.request.url).replace('.json', '')}: failed with code: {exc.response.status_code}; "
            f"{'Please authenticate' if exc.response.status_code == 403 else 'Please try again later'}")


class Session(HasOptions):
    """API клиент сессия """

    def __init__(self, cs: HasOptions | None = None, **options):
        assert isinstance(cs, HasOptions) or len(options)
        if cs is not None:
            options.update(cs.options)
        super().__init__(**options)
        self._client = None

    def __enter__(self) -> Client:
        self._client = Client(True, **self.options)
        self._client.httpx_cli.__enter__()
        return self._client

    def __exit__(self, *exc_info):
        return self._client.httpx_cli.__exit__(*exc_info)

    async def __aenter__(self) -> Client:
        self._client = Client(False, **self.options)
        await self._client.httpx_cli.__aenter__()
        return self._client

    async def __aexit__(self, *exc_info):
        return await self._client.httpx_cli.__aexit__(*exc_info)


def authorize(username: str, password: str) -> bool:
    """Авторизация сессии по умолчанию

    Parameters
    ----------
    username: str
        Имя пользователя
    password: str
        Пароль

    Returns
    -------
    bool
        True, если авторизация успешна, иначе False
    """
    global AUTH_CERT
    with Session(auth_cert=AUTH_CERT) as client:
        if auth_cert := client.authorize(username, password):
            AUTH_CERT = auth_cert
            return True
        return False


def __getattr__(name):
    if name == 'default':
        return Session(auth_cert=AUTH_CERT)


def data_gen(cs: Session, path: str, options, offset, limit, section='data'):
    start = offset
    with Session(cs or Session(auth_cert=AUTH_CERT)) as client:
        while True:
            options['start'] = start
            items = client.get_objects(path, lambda data: result_deserializer(data, section), **options)
            if metrics := items.get(section):
                for item in metrics:
                    yield item
                    start += 1
                    if (start - offset) >= limit:
                        return
            else:
                return
