import typing as t
from datetime import date

from moexalgo.features.common import CommonTicker, CommonMarket
from moexalgo.session import Session
from moexalgo.utils import (
    DataFrame,
    result_adapter,
    prepare_from_till_dates,
    calc_offset_limit,
    normalize_data,
)


class AlgopackMarketMixin:
    """
    Миксин добавляющий методы Algopack обобщенному классу `Market`.
    """

    def tradestats(
        self: CommonMarket,
        *,
        date: str | date = None,
        latest: bool = None,
        offset: int = None,
        native: bool = False,
    ) -> t.Iterable[dict[str, t.Any]] | DataFrame:
        """
        Возвращает метрики `TradeStat` по заданным параметрам.

        Parameters
        ----------
        date :
            Дата данных. Если не указано, данные выдаются за сегодняшнее число.
        latest :
            Включает режим выдачи последних записей в наборе.
        offset :
            Начальная позиция в последовательности записей.
        native :
            Если флаг выставлен в `True` всегда возвращается итератор словарей.
        """
        path = self._get_path_for("algopack")
        date, _ = prepare_from_till_dates(date, date)
        offset, limit = calc_offset_limit(offset, 50_000)
        options = dict(date=date, offset=offset, limit=limit)
        if latest:
            options["latest"] = 1
        return result_adapter(fetch_algopack(path, "tradestats", **options), native)

    def orderstats(
        self: CommonMarket,
        *,
        date: str | date = None,
        latest: bool = None,
        offset: int = None,
        native: bool = False,
    ) -> t.Iterable[dict[str, t.Any]] | DataFrame:
        """
        Возвращает метрики `OrderStat` по заданным параметрам.

        Parameters
        ----------
        date :
            Дата данных. Если не указано, данные выдаются за сегодняшнее число.
        latest :
            Включает режим выдачи последних записей в наборе.
        offset :
            Начальная позиция в последовательности записей.
        native :
            Если флаг выставлен в `True` всегда возвращается итератор словарей.
        """
        path = self._get_path_for("algopack")
        date, _ = prepare_from_till_dates(date, date)
        offset, limit = calc_offset_limit(offset, 50_000)
        options = dict(date=date, offset=offset, limit=limit)
        if latest:
            options["latest"] = 1
        return result_adapter(fetch_algopack(path, "orderstats", **options), native)

    def obstats(
        self: CommonMarket,
        *,
        date: str | date = None,
        latest: bool = None,
        offset: int = None,
        native: bool = False,
    ) -> t.Iterable[dict[str, t.Any]] | DataFrame:
        """
        Возвращает метрики `ObStat` по заданным параметрам.

        Parameters
        ----------
        date :
            Дата данных. Если не указано, данные выдаются за сегодняшнее число.
        latest :
            Включает режим выдачи последних записей в наборе.
        offset :
            Начальная позиция в последовательности записей.
        native :
            Если флаг выставлен в `True` всегда возвращается итератор словарей.
        """
        path = self._get_path_for("algopack")
        date, _ = prepare_from_till_dates(date, date)
        offset, limit = calc_offset_limit(offset, 50_000)
        options = dict(date=date, offset=offset, limit=limit)
        if latest:
            options["latest"] = 1
        return result_adapter(fetch_algopack(path, "obstats", **options), native)

    def alerts(
        self: CommonMarket,
        *,
        date: str | date = None,
        latest: bool = None,
        offset: int = None,
        native: bool = False,
    ) -> t.Iterable[dict[str, t.Any]] | DataFrame:
        """
        Возвращает MegaAlert (оповещение об аномальной рыночной активности) по заданным параметрам.

        Parameters
        ----------
        date :
            Дата данных. Если не указано, данные выдаются за сегодняшнее число.
        latest :
            Включает режим выдачи последних записей в наборе.
        offset :
            Начальная позиция в последовательности записей.
        native :
            Если флаг выставлен в `True` всегда возвращается итератор словарей.
        """
        path = self._get_path_for("algopack")
        date, _ = prepare_from_till_dates(date, date)
        offset, limit = calc_offset_limit(offset, 50_000)
        options = dict(date=date, offset=offset, limit=limit)
        if latest:
            options["latest"] = 1
        return result_adapter(fetch_algopack(path, "alerts", **options), native)

    def hi2(
        self: CommonMarket,
        *,
        date: str | date = None,
        latest: bool = None,
        offset: int = None,
        native: bool = False,
    ) -> t.Iterable[dict[str, t.Any]] | DataFrame:
        """
        Возвращает метрики `Hi2` (индекс рыночной концентрации) по заданным параметрам.

        Parameters
        ----------
        date :
            Дата данных. Если не указано, данные выдаются за сегодняшнее число.
        latest :
            Включает режим выдачи последних записей в наборе.
        offset :
            Начальная позиция в последовательности записей.
        native :
            Если флаг выставлен в `True` всегда возвращается итератор словарей.
        """
        path = self._get_path_for("algopack")
        date, _ = prepare_from_till_dates(date, date)
        offset, limit = calc_offset_limit(offset, 50_000)
        options = dict(date=date, offset=offset, limit=limit)
        if latest:
            options["latest"] = 1
        return result_adapter(fetch_algopack(path, "hi2", **options), native)


class AlgopackTickerMixin:
    """
    Миксин добавляющий методы Algopack обобщенному классу `Ticker`.
    """

    def tradestats(
        self: CommonTicker,
        *,
        start: str | date = None,
        end: str | date = None,
        latest: bool = None,
        offset: int = None,
        native: bool = False,
    ) -> t.Iterable[dict[str, t.Any]] | DataFrame:
        """
        Возвращает метрики `TradeStat` по заданным параметрам.

        Parameters
        ----------
        start :
            Дата начала диапазона выдачи данных. (`start` может быть равен `end`, тогда вернутся записи за один день)
        end :
            Дата конца диапазона выдачи данных.
        latest :
            Включает режим выдачи последних записей в наборе.
        offset :
            Начальная позиция в последовательности записей.
        native :
            Если флаг выставлен в `True` всегда возвращается итератор словарей.
        """
        path = self.market._get_path_for("algopack")
        from_date, till_date = prepare_from_till_dates(start, end)
        offset, limit = calc_offset_limit(offset, 10_000)
        options = dict(**{"from": from_date, "till": till_date}, offset=offset, limit=limit)
        if latest:
            options["latest"] = 1
        return result_adapter(fetch_algopack(path, "tradestats", self.secid, **options), native)

    def orderstats(
        self: CommonTicker,
        *,
        start: str | date = None,
        end: str | date = None,
        latest: bool = None,
        offset: int = None,
        native: bool = False,
    ) -> t.Iterable[dict[str, t.Any]] | DataFrame:
        """
        Возвращает метрики `OrderStat` по заданным параметрам.

        Parameters
        ----------
        start :
            Дата начала диапазона выдачи данных. (`start` может быть равен `end`, тогда вернутся записи за один день)
        end :
            Дата конца диапазона выдачи данных.
        latest :
            Включает режим выдачи последних записей в наборе.
        offset :
            Начальная позиция в последовательности записей.
        native :
            Если флаг выставлен в `True` всегда возвращается итератор словарей.
        """
        path = self.market._get_path_for("algopack")
        from_date, till_date = prepare_from_till_dates(start, end)
        offset, limit = calc_offset_limit(offset, 10_000)
        options = dict(**{"from": from_date, "till": till_date}, offset=offset, limit=limit)
        if latest:
            options["latest"] = 1
        return result_adapter(fetch_algopack(path, "orderstats", self.secid, **options), native)

    def obstats(
        self: CommonTicker,
        *,
        start: str | date = None,
        end: str | date = None,
        latest: bool = None,
        offset: int = None,
        native: bool = False,
    ) -> t.Iterable[dict[str, t.Any]] | DataFrame:
        """
        Возвращает метрики `ObStat` по заданным параметрам.

        Parameters
        ----------
        start :
            Дата начала диапазона выдачи данных. (`start` может быть равен `end`, тогда вернутся записи за один день)
        end :
            Дата конца диапазона выдачи данных.
        latest :
            Включает режим выдачи последних записей в наборе.
        offset :
            Начальная позиция в последовательности записей.
        native :
            Если флаг выставлен в `True` всегда возвращается итератор словарей.
        """
        path = self.market._get_path_for("algopack")
        from_date, till_date = prepare_from_till_dates(start, end)
        offset, limit = calc_offset_limit(offset, 10_000)
        options = dict(**{"from": from_date, "till": till_date}, offset=offset, limit=limit)
        if latest:
            options["latest"] = 1
        return result_adapter(fetch_algopack(path, "obstats", self.secid, **options), native)

    def alerts(
        self: CommonTicker,
        *,
        start: str | date = None,
        end: str | date = None,
        latest: bool = None,
        offset: int = None,
        native: bool = False,
    ) -> t.Iterable[dict[str, t.Any]] | DataFrame:
        """
        Возвращает MegaAlert (оповещение об аномальной рыночной активности) по заданным параметрам.

        Parameters
        ----------
        start :
            Дата начала диапазона выдачи данных. (`start` может быть равен `end`, тогда вернутся записи за один день)
        end :
            Дата конца диапазона выдачи данных.
        latest :
            Включает режим выдачи последних записей в наборе.
        offset :
            Начальная позиция в последовательности записей.
        native :
            Если флаг выставлен в `True` всегда возвращается итератор словарей.
        """
        path = self.market._get_path_for("algopack")
        from_date, till_date = prepare_from_till_dates(start, end)
        offset, limit = calc_offset_limit(offset, 10_000)
        options = dict(**{"from": from_date, "till": till_date}, offset=offset, limit=limit)
        if latest:
            options["latest"] = 1
        return result_adapter(fetch_algopack(path, "alerts", self.secid, **options), native)

    def hi2(
        self: CommonTicker,
        *,
        start: str | date = None,
        end: str | date = None,
        latest: bool = None,
        offset: int = None,
        native: bool = False,
    ) -> t.Iterable[dict[str, t.Any]] | DataFrame:
        """
        Возвращает метрики `Hi2` (индекс рыночной концентрации) по заданным параметрам.

        Parameters
        ----------
        start :
            Дата начала диапазона выдачи данных. (`start` может быть равен `end`, тогда вернутся записи за один день)
        end :
            Дата конца диапазона выдачи данных.
        latest :
            Включает режим выдачи последних записей в наборе.
        offset :
            Начальная позиция в последовательности записей.
        native :
            Если флаг выставлен в `True` всегда возвращается итератор словарей.
        """
        path = self.market._get_path_for("algopack")
        from_date, till_date = prepare_from_till_dates(start, end)
        offset, limit = calc_offset_limit(offset, 10_000)
        options = dict(**{"from": from_date, "till": till_date}, offset=offset, limit=limit)
        if latest:
            options["latest"] = 1
        return result_adapter(fetch_algopack(path, "hi2", self.secid, **options), native)


def fetch_algopack(
    path: str,
    metrics: str,
    secid: str = None,
    limit: int = 10_000,
    offset: int = 0,
    **options: t.Any,
):
    with Session() as client:
        start = offset
        while True:
            options["start"] = start
            if data := normalize_data(
                client.get_objects(
                    f"{path}/{metrics}/{secid}" if secid else f"{path}/{metrics}", lambda data: data["data"], **options
                )
            ):
                for item in data:
                    yield item
                    start += 1
                if (start - offset) < limit and limit > 0:
                    continue
            break
