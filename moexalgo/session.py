from __future__ import annotations

import asyncio
from time import time, sleep
from typing import Callable, Iterator, Optional, Union

import httpx

from moexalgo.utils import json, result_deserializer

BASE_URL = 'https://iss.moex.com/iss'
TOKEN_URL = 'https://apim.moex.com/iss'
AUTH_URL = 'https://passport.moex.com/authenticate'
AUTH_CERT = None
USE_HTTPS = True
TOKEN = None
_NEXT_REQUEST_AT = 0
_REQUEST_TIMEOUT = 0.1


class HasOptions:
    """
    Базовый класс для объектов с опциями.

    Attributes
    ----------
    options : dict
        Опционные параметры.
    """

    def __init__(self, auth_cert: str = None, base_url: str = None, timeout: int = 300, **options) -> None:
        """
        Parameters
        ----------
        auth_cert : str
            Сертификат авторизации.
        base_url : str
            Базовый URL.
        timeout : int
            Таймаут
        options : dict
            Опционные параметры.

        Returns
        -------
        return : None
        """
        global TOKEN
        base_url = base_url or BASE_URL
        if TOKEN:
            base_url = TOKEN_URL
            if 'headers' not in options:
                options['headers'] = []
            if not [name for name, _ in options['headers'] if name=='Authorization']:
                options['headers'].append(('Authorization', f'Bearer {TOKEN}'))
        if base_url.startswith('http:') and USE_HTTPS:
            base_url = base_url.replace('http:', 'https:')
        elif base_url.startswith('https:') and not USE_HTTPS:
            base_url = base_url.replace('https:', 'http:')
            options['verify'] = False

        self.__options = dict(**options, base_url=base_url, timeout=timeout)
        if auth_cert:
            self.__options.setdefault('cookies', {})['MicexPassportCert'] = auth_cert

    @property
    def options(self) -> dict:
        """
        Опционные параметры использованные при создании сессии/клиента.

        Returns
        -------
        return : dict
            Опционные параметры.
        """
        return self.__options


class Client(HasOptions):
    """
    Клиент для работы с API.

    Attributes
    ----------
    sync : bool
        Синхронный режим работы.
    authorized : bool
        Авторизован ли клиент.
    httpx_cli : httpx.Client | httpx.AsyncClient
        Клиент для работы с HTTP.
    """

    def __init__(self, sync: bool = True, **options) -> None:
        """
        Parameters
        ----------
        sync : bool
            Синхронный режим работы.
        options : dict
            Опционные параметры.
        
        Returns
        -------
        return : None
        """
        options.update(follow_redirects = True,
                       headers = [('User-Agent', 'python-httpx/moexalgo')])
        super().__init__(**options)
        self.httpx_cli = httpx.Client(**self.options) if sync else httpx.AsyncClient(**self.options)

    @property
    def sync(self) -> bool:
        """
        Синхронный режим работы клиента.

        Returns
        -------
        return : bool
            `True` если клиент синхронный, иначе `False`.
        """
        return isinstance(self.httpx_cli, httpx.Client)

    @property
    def authorized(self) -> bool:
        """
        Авторизован ли клиент.

        Returns
        -------
        return : bool
            `True` если клиент авторизован, иначе `False`.
        """
        return bool(self.options.get('auth_cert'))

    def authorize(self, username: str, password: str) -> Optional[str]:
        """
        Авторизация клиента.

        Parameters
        ----------
        username : str
            Имя пользователя.
        password : str
            Пароль пользователя.

        Returns
        -------
        return : Optional[str]
            Сертификат авторизации или None, если авторизация не удалась.
        """

        def _process_response(resp: httpx.Response) -> Optional[str]:
            """
            Обработка ответа авторизации.

            Parameters
            ----------
            resp : httpx.Response
                Ответ авторизации.
            
            Returns
            -------
            return : Optional[str]
                Сертификат авторизации или None, если авторизация не удалась.
            """
            if resp.is_success:
                return resp.cookies.get('MicexPassportCert', self.options.get('cookies', {}).get('MicexPassportCert'))
            return None

        async def _async_authorize() -> Optional[str]:
            """
            Асинхронная авторизация.

            Returns
            -------
            return : Optional[str]
                Сертификат авторизации или None, если авторизация не удалась.
            """
            return _process_response(await self.httpx_cli.get(AUTH_URL, auth=(username, password)))

        def _sync_authorize() -> Optional[str]:
            """
            Синхронная авторизация.

            Returns
            -------
            return : Optional[str]
                Сертификат авторизации или None, если авторизация не удалась.
            """
            return _process_response(self.httpx_cli.get(AUTH_URL, auth=(username, password)))

        self.options['auth_cert'] = _sync_authorize() if self.sync else _async_authorize()
        return self.options['auth_cert']

    def get_objects(self, path: str, deserializer: Callable[[dict], dict | list], **params) -> Union[dict, list]:
        """
        Получение объектов по переданному адресу.

        Parameters
        ----------
        path : str
            Путь к объектам.
        deserializer: callable
            Функция десериализации.
        params : dict
            Параметры запроса.

        Returns
        -------
        return : Union[dict, list]
            Объекты или список объектов.

        Raises
        ------
        httpx.HTTPStatusError
            Вызывается, если запрос завершился неудачно.
        ValueError
            Вызывается, если получен неверный ответ.
        """

        global _NEXT_REQUEST_AT

        def _parse_response(resp: httpx.Response) -> Union[dict, list]:
            """
            Парсинг ответа.

            Parameters
            ----------
            resp : httpx.Response
                Ответ запроса.

            Returns
            -------
            return : Union[dict, list]
                Объекты или список объектов.
            """
            if not resp.is_success:
                resp.raise_for_status()
            if not resp.headers['content-type'].startswith('application/json'):
                resp.status_code = 403
                resp.raise_for_status()
            if data := json.loads(resp.text):
                return deserializer(data)
            raise ValueError('Received wrong data')

        async def _async_get_objects(timeout: float) -> Union[dict, list]:
            """
            Асинхронное получение объектов.

            Parameters
            ----------
            timeout : float
                Таймаут (время ожидания).
            
            Returns
            -------
            return : Union[dict, list]
                Объекты или список объектов.
            """
            if timeout:
                await asyncio.sleep(timeout)
            return _parse_response(await self.httpx_cli.get(url, params=params))

        def _sync_get_objects(timeout: float) -> Union[dict, list]:
            """
            Синхронное получение объектов.

            Parameters
            ----------
            timeout : float
                Таймаут (время ожидания).
            
            Returns
            -------
            return : Union[dict, list]
                Объекты или список объектов.
            """
            if timeout:
                sleep(timeout)
            return _parse_response(self.httpx_cli.get(url, params=params))

        path = [item for item in path.split('/') if item.strip()]
        url = '/'.join(path) + '.json'

        timeout = _NEXT_REQUEST_AT - time()
        if self.authorized or timeout <= 0:
            timeout = 0.2
        _NEXT_REQUEST_AT = time() + _REQUEST_TIMEOUT + timeout

        return _sync_get_objects(timeout) if self.sync else _async_get_objects(timeout)

    @staticmethod
    def format_error(exc: httpx.HTTPStatusError) -> str:
        """
        Форматирование ошибки.

        Parameters
        ----------
        exc : httpx.HTTPStatusError
            Исключение HTTP.
        
        Returns
        -------
        return : str
            Сообщение об ошибке и рекомендации.
        """
        url = str(exc.request.url).replace('.json', '')
        main_msg = f'HTTP request to {url}: failed with code: {exc.response.status_code};'
        recommendations = 'Please authenticate' if exc.response.status_code == 403 else 'Please try again later'
        return ' '.join([main_msg, recommendations])


class Session(HasOptions):
    """
    Сессия для работы с API.

    Attributes
    ----------
    _client : Client
        Клиент для работы с API.
    """

    def __init__(self, cs: HasOptions = None, **options) -> None:
        """
        Parameters
        ----------
        cs : HasOptions | None
            Сессия, из которой будут взяты опции, by default None.
        options : dict
            Опционные параметры сессии.
        
        Returns
        -------
        return : None
        """
        assert isinstance(cs, HasOptions) or len(options)
        if cs is not None:
            options.update(cs.options)
        super().__init__(**options)
        self._client = None

    def __enter__(self) -> Client:
        """
        Вход в сессию.

        Returns
        -------
        return : Client
            Клиент для работы с API.
        """
        self._client = Client(True, **self.options)
        self._client.httpx_cli.__enter__()
        return self._client

    def __exit__(self, *exc_info) -> bool:
        """
        Выход из сессии.

        Parameters
        ----------
        exc_info : tuple
            Информация об исключении.
        
        Returns
        -------
        return : bool
            `True`, если исключение обработано, иначе `False`.
        """
        return self._client.httpx_cli.__exit__(*exc_info)

    async def __aenter__(self) -> Client:
        """
        Асинхронный вход в сессию.

        Returns
        -------
        return : Client
            Клиент для работы с API.
        """
        self._client = Client(False, **self.options)
        await self._client.httpx_cli.__aenter__()
        return self._client

    async def __aexit__(self, *exc_info):
        return await self._client.httpx_cli.__aexit__(*exc_info)


def authorize(username: str, password: str) -> bool:
    """
    Авторизация сессии по умолчанию.

    Parameters
    ----------
    username : str
        Имя пользователя.
    password : str
        Пароль пользователя.

    Returns
    -------
    return : bool
        `True`, если авторизация прошла успешно, иначе `False`.
    """
    global AUTH_CERT
    with Session(auth_cert=AUTH_CERT) as client:
        if auth_cert := client.authorize(username, password):
            AUTH_CERT = auth_cert
            return True
        return False


def __getattr__(name: str) -> Session:
    """
    Получение сессии по имени.

    Parameters
    ----------
    name : str
        Имя сессии.
    
    Returns
    -------
    return : Session
        Сессия с указанным именем.
    """
    if name == 'default':
        return Session(auth_cert=AUTH_CERT)


def data_gen(cs: Session,
             path: str,
             options: dict,
             offset: int,
             limit: int,
             section: str = 'data') -> Optional[Iterator[dict]]:
    """
    Генератор данных.

    Parameters
    ----------
    cs : Session
        Сессия клиента.
    path : str
        Путь к данным.
    options : dict
        Опции запроса.
    offset : int
        Смещение данных.
    limit : int
        Лимит данных.
    section : str, optional
        Секция данных, by default 'data'.
    
    Returns
    -------
    return : Optional[Iterator[dict]]
        Итератор с данными или None, если данных нет.
    """
    start = offset
    with Session(cs or Session(auth_cert=AUTH_CERT)) as client:
        while True:
            options['start'] = start
            items = client.get_objects(path, lambda data: result_deserializer(data, section), **options)
            if metrics := items.get(section):
                for item in metrics:
                    yield item
                    start += 1
                    if (start - offset) >= limit and limit > 0:
                        return
                if limit < 0:
                    return
            else:
                return
