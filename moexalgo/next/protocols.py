import sys
import typing as t
from datetime import date
from enum import Enum
from types import ModuleType

if "ipykernel" in sys.modules:
    from pandas import DataFrame
else:
    type DataFrame = t.Any


class CandlePeriod(Enum):
    """
    Возможные временные интервалы для свечей.
    """

    ONE_MINUTE = 1
    TEN_MINUTES = 10
    ONE_HOUR = 60
    ONE_DAY = 24
    ONE_WEEK = 7
    ONE_MONTH = 31


class Market(t.Protocol):
    """
    Протокол объекта `moexalgo.Market`
    """

    module: ModuleType

    def tickers(
        self,
        *fields: str,
        all_fields: bool = False,
        native: bool = False,
    ) -> t.Iterable[dict[str, t.Any]] | DataFrame:
        """
        Информация о всех инструментах рынка.

        Parameters
        ----------
        fields : tuple[str]
            Поля для отображения
        all_fields : bool, optional
            Если флаг выставлен в `True` выводятся все имеющиеся поля.
        native : bool, optional
            Если флаг выставлен в `True` всегда возвращается итератор словарей.

        Returns
        -------
        return : Union[list[dict], pd.DataFrame]
            При использовании в среде Jupiter Notebook по умалчиванию данные возвращаются в виде `DataFrame`.
            Используйте флаг `native` что бы отменить такое поведение.
        """

    def marketdata(
        self,
        *fields: str,
        all_fields: bool = False,
        native: bool = False,
    ) -> t.Iterable[dict[str, t.Any]] | DataFrame:
        """
        Статистическая информация о всех инструментах рынка.

        Parameters
        ----------
        fields : tuple[str]
            Поля для отображения
        all_fields : bool, optional
            Если флаг выставлен в `True` выводятся все имеющиеся поля.
        native : bool, optional
            Если флаг выставлен в `True` всегда возвращается итератор словарей.

        Returns
        -------
        return : Union[list[dict], pd.DataFrame]
            При использовании в среде Jupiter Notebook по умалчиванию данные возвращаются в виде `DataFrame`.
            Используйте флаг `native` что бы отменить такое поведение.
        """


class Ticker(t.Protocol):
    """
    Протокол объекта `moexalgo.Ticker`
    """

    def info(self, *fields: str, all_fields: bool = False, native: bool = False) -> dict[str, t.Any] | DataFrame:
        """
        Информация об инструменте.

        Parameters
        ----------
        fields : tuple[str]
            Поля для отображения
        all_fields : bool, optional
            Если флаг выставлен в `True` выводятся все имеющиеся поля.
        native : bool, optional
            Если флаг выставлен в `True` всегда возвращается словарь.

        Returns
        -------
        return : dict | pd.DataFrame
            При использовании в среде Jupiter Notebook по умалчиванию данные возвращаются в виде `DataFrame`.
            Используйте флаг `native` что бы отменить такое поведение.
        """

    def candles(
        self,
        start: str | date,
        end: str | date,
        period: int | str | CandlePeriod = None,
        *,
        offset: int = 0,
        latest: bool = False,
        native: bool = False,
    ) -> t.Iterable[dict[str, t.Any]] | DataFrame:
        """
        Возвращает свечи инструмента по заданным параметрам.

        Parameters
        ----------
        start : Union[str, date]
            Дата начала диапазона выдачи данных. (`start` может быть равен `end`, тогда вернутся записи за один день)
        end : Union[str, date]
            Дата конца диапазона выдачи данных.
        period : Union[str, int, CandlePeriod], optional
            Период свечи, by default None.

            Если `int`, то интерпретируется в следующем формате:
            - 1 - 1 минута
            - 10 - 10 минут
            - 60 - 1 час
            - 24 - 1 день
            - 7 - 1 неделя
            - 31 - 1 месяц

            Если `str`, то интерпретируется в следующем формате:
            - '1min' - 1 минута
            - '10min' - 10 минут
            - '1h' - 1 час
            - '1d' - 1 день
            - '1w' - 1 неделя
            - '1m' - 1 месяц

        offset : int, optional
            Начальная позиция в последовательности записей, by default 0.
        latest : bool, optional
            Включает режим выдачи последних `latest` записей в наборе, by default False.
        native : bool, optional
            Если флаг выставлен в `True` всегда возвращается итератор словарей.

        Returns
        -------
        return : t.Iterable[dict[str, t.Any]] | DataFrame
            При использовании в среде Jupiter Notebook по умалчиванию данные возвращаются в виде `DataFrame`.
            Используйте флаг `native` что бы отменить такое поведение.
        """

    def trades(
        self,
        tradeno: int = None,
        *,
        offset: int = 0,
        latest: bool = False,
        native: bool = False,
    ) -> t.Iterable[dict[str, t.Any]] | DataFrame:
        """
        Возвращает сделки за последний день или начиная с заданного `tradeno`.

        Parameters
        ----------
        tradeno : int, optional
            Номер сделки с которого выдаются данные, если не задано, то с начала дня.
        native : bool, optional
            Если флаг выставлен в `True` всегда возвращается итератор словарей.

        Returns
        -------
        return : t.Iterable[dict[str, t.Any]] | DataFrame
            При использовании в среде Jupiter Notebook по умалчиванию данные возвращаются в виде `DataFrame`.
            Используйте флаг `native` что бы отменить такое поведение.
        """

    def orderbook(
        self,
        native: bool = False,
    ) -> t.Iterable[dict[str, t.Any]] | DataFrame:
        """
        Возвращает текущий стакан лучших цен.

        Parameters
        ----------
        native : bool, optional
            Если флаг выставлен в `True` всегда возвращается итератор словарей.

        Returns
        -------
        return : t.Iterable[dict[str, t.Any]] | DataFrame
            При использовании в среде Jupiter Notebook по умалчиванию данные возвращаются в виде `DataFrame`.
            Используйте флаг `native` что бы отменить такое поведение.
        """
