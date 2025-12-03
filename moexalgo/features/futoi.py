import typing as t
from datetime import date

from moexalgo.features.common import CommonMarket, CommonTicker
from moexalgo.session import Session
from moexalgo.utils import result_adapter, normalize_data, prepare_from_till_dates

type DataFrame = t.Any
PERPETUAL = ("USDRUBF", "EURRUBF", "CNYRUBF", "IMOEXF", "GLDRUBF", "SBERF", "GAZPF")


class FutOIMarketMixin:
    """
    Миксин добавляющий метод `futoi` обобщенному классу `Market`.
    """

    def futoi(
        self: CommonMarket,
        *,
        date: str | date = None,
        # latest: bool = None,
        # offset: int = None,
        native: bool = False,
    ) -> t.Iterable[dict[str, t.Any]] | DataFrame:
        """
        Возвращает метрики `FUTOI` по заданным параметрам.

        Parameters
        ----------
        date :
            Дата данных. Если не указано, данные выдаются за сегодняшнее число.
        native :
            Если флаг выставлен в `True` возвращается итератор словарей.
        """
        path = self._get_path_for("futoi")
        date, _ = prepare_from_till_dates(date, date)
        options = dict[str, t.Any](date=date)
        # if latest:
        #     options["latest"] = 1
        # offset, limit = calc_offset_limit(offset, 10_000)
        # options = dict(options, offset=offset, limit=limit)
        options = dict(options, offset=0, limit=-1)
        return result_adapter(fetch_futoi(path, **options), native)


class FutOITickerMixin:
    """
    Миксин добавляющий метод `futoi` обобщенному классу `Ticker`.
    """

    def futoi(
        self: CommonTicker,
        *,
        start: str | date = None,
        end: str | date = None,
        # latest: bool = None,
        # offset: int = None,
        native: bool = False,
    ) -> t.Iterable[dict[str, t.Any]] | DataFrame:
        """
        Возвращает метрики `FUTOI` по заданным параметрам.

        Parameters
        ----------
        start :
            Дата начала диапазона выдачи данных. (`start` может быть равен `end`, тогда вернутся записи за один день)
        end :
            Дата конца диапазона выдачи данных.
        native :
            Если флаг выставлен в `True` возвращается итератор словарей.
        """
        path = self.market._get_path_for("futoi")
        from_date, till_date = prepare_from_till_dates(start, end)
        options: dict[str, t.Any] = {"from": from_date, "till": till_date}
        # if latest:
        #     options["latest"] = 1
        # offset, limit = calc_offset_limit(offset, 10_000)
        # options = dict(options, offset=offset, limit=limit)
        options = dict(options, offset=0, limit=-1)
        if not hasattr(self, "_tickers"):
            self._sectypes = dict(
                (item["secid"], item["sectype"]) for item in self.market.tickers("secid", "sectype", native=True)
            )
        if self.secid not in PERPETUAL:
            sectype = self._sectypes.get(self.secid, None)
        else:
            sectype = self.secid
        if not sectype:
            raise KeyError(f"sectype for secid: {self.secid} not found")
        return result_adapter(fetch_futoi(path, sectype, **options), native)


def fetch_futoi(
    path: str,
    secid: str = None,
    limit: int = 10_000,
    offset: int = 0,
    **options: t.Any,
):
    wa, limit = (True, 1000) if limit <= 0 else (False, limit)
    with Session() as client:
        start = offset
        while True:
            options["start"] = start
            if data := normalize_data(
                client.get_objects(f"{path}/{secid}" if secid else f"{path}", lambda data: data["futoi"], **options)
            ):
                for item in data:
                    yield item
                    start += 1
                else:
                    if wa:
                        break
                if (start - offset) < limit and limit > 0:
                    continue
            break
