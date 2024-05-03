import decimal
import json as _json
from datetime import datetime, date, time
from enum import Enum


class ISSTickerParamException(Exception):
    """
    Исключение, возникающее при отсутствии параметра `ticker`.

    Attributes
    ----------
    message : str
        Сообщение об ошибке
    """

    def __init__(self, message: str = "The start and end parameters are required") -> None:
        self.message = message
        super().__init__(self.message)


class ISSDateParamException(Exception):
    """
    Исключение, возникающее при некорректном формате даты.

    Attributes
    ----------
    message : str
        Сообщение об ошибке
    """

    def __init__(self, message: str = "start must be less than or equal to end.") -> None:
        """
        Parameters
        ----------
        message : str
            Сообщение об ошибке
        
        Returns
        -------
        return : None
        """
        self.message = message
        super().__init__(self.message)


class CandlePeriod(Enum):
    """
    Временные интервалы для свечей.

    Attributes
    ----------
    ONE_MINUTE : int
        1 минута
    TEN_MINUTES : int
        10 минут
    ONE_HOUR : int
        1 час = 60 минут
    ONE_DAY : int
        1 день = 24 часа
    ONE_WEEK : int
        1 неделя = 7 дней
    ONE_MONTH : int
        1 месяц = 31 день
    """
    ONE_MINUTE = 1
    TEN_MINUTES = 10
    ONE_HOUR = 60
    ONE_DAY = 24
    ONE_WEEK = 7
    ONE_MONTH = 31


class RequiredImport:
    """
    Класс для импорта библиотеки, если она не была установлена.

    Attributes
    ----------
    __name : str
        Название библиотеки (модуля).
    """

    def __init__(self, name: str) -> None:
        """
        Parameters
        ----------
        name : str
            Название библиотеки.
        
        Returns
        -------
        return : None
        """
        self.__name = name

    def __getattr__(self, item: str) -> None:
        """
        Parameters
        ----------
        item : str
            Название атрибута.
        
        Returns
        -------
        return : None
        """
        raise ImportError(f'Required `{self.__name}`')


try:
    import pandas as pd
except ImportError:
    pandas = RequiredImport('pandas')


class json:
    """
    Класс для работы с JSON.

    Attributes
    ----------
    loads : Callable
        Загрузка JSON.
    JSONDecodeError : Exception
        Исключение при ошибке декодирования JSON.
    dumps : Callable
        Сохранение JSON.
    """
    loads = _json.loads
    JSONDecodeError = _json.JSONDecodeError

    @staticmethod
    def dumps(*args, **kwargs) -> str:
        """
        Parameters
        ----------
        args : Any
            Аргументы.
        kwargs : Any
            Ключевые аргументы.
        
        Returns
        -------
        return : str
            Строка JSON.
        """

        def default(obj: object) -> object:
            """
            Параметры по умолчанию для преобразования объектов в JSON.

            Parameters
            ----------
            obj : object
                Объект данных.

            Returns
            -------
            return : object
                Объект данных.
            """
            if isinstance(obj, decimal.Decimal):
                return float(str(obj))
            elif isinstance(obj, (datetime, date, time)):
                return obj.isoformat()
            
            raise TypeError

        return _json.dumps(*args, **kwargs, default=default)


def result_deserializer(data: dict, *sections, key: callable = None) -> dict:
    """
    Parameters
    ----------
    data : dict
        Слоаврь с данными от ISS.
    sections : Tuple
        Секции данных, by default ('securities', 'marketdata').
    key : Callable
        Ключевая функция, которая принимает элемент данных и возвращает ключ, by default None.

    Returns
    -------
    return : dict
        Словарь с данными.
    """
    result = dict()

    sections = sections or ('securities', 'marketdata')
    for section in sections:
        metadata = data[section]['metadata']
        columns = data[section]['columns']

        for values in data[section]['data']:
            item = item_normalizer(metadata, dict(zip(columns, values)))

            if key:
                result.setdefault(section, dict())[key(item)] = item
            else:
                result.setdefault(section, list()).append(item)
    
    return result


def item_normalizer(metadata: dict, item: dict) -> dict:
    """
    Нормализация данных.

    Parameters
    ----------
    metadata : dict
        Метаданные.
    item : dict
        Элемент данных.
    
    Notes
    -----
    `lambda s: …` - очень дорогая операция на больших данных без numpy.

    Returns
    -------
    return : dict
        Словарь с нормализованными данными.
    """
    conv = {
        'int32': lambda s: int(s) if s is not None else None,
        'int64': lambda s: int(s) if s is not None else None,
        'double': lambda s: float(s) if s is not None else None,
        'date': lambda s: date.fromisoformat(s.strip()) if (s is not None) and (s != '0000-00-00') else None,
        'datetime': lambda s: datetime.fromisoformat(s.strip()) if s is not None else None,
        'time': lambda s: time.fromisoformat(s.strip()) if s is not None else None
    }
    return dict((key, conv.get(metadata[key]['type'], str)(value)) for key, value in item.items())
