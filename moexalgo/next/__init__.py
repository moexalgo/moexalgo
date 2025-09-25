import sys
from datetime import date
from types import ModuleType

import moexalgo.next.engines.currency
import moexalgo.next.engines.futures
import moexalgo.next.engines.stock
from moexalgo.next import engines
from moexalgo.next import protocols
from moexalgo.session import Session


def Market(name: str, board: str = None) -> protocols.Market:
    """
    Представление раздела биржевого рынка.

    Parameters
    ----------
    name : str
        Название рынка или его символическое имя.
    board : str, optional
        Идентификатор, указывающий на специфическую торговую площадку или сегмент рынка.
        Если не указано, автоматически определятся первичный идентификатор на основе общих правил.
    """
    RESOLVE_MAP = {
        (engines.currency, "selt", "CETS"): ["selt", "currency", "fx"],
        (engines.stock, "shares", "TQBR"): ["shares", "stocks", "equity", "eq"],
        (engines.stock, "index", "SNDX"): ["index"],
        (engines.stock, "bonds", "TQOB"): ["bonds"],
        (engines.futures, "forts", "RFUD"): ["futures", "forts", "fo"],
        (engines.futures, "options", "ROPD"): ["options"],
    }

    def resolve(name: str, boardid: str | None) -> tuple[ModuleType, str, str]:
        for (module, market, default_boardid), aliases in RESOLVE_MAP.items():
            if name in aliases:
                return module, market, boardid or default_boardid
        raise LookupError(f"Unrecognized market' name '{name}'")

    module, name, boardid = resolve(name.lower(), board.upper() if board else None)
    return getattr(module, "Market")(name, boardid)


def Ticker(name: str, board: str = None) -> protocols.Ticker:
    """
    Представление конкретного финансового инструмента.

    Parameters
    ----------
    name : str
        Тикер финансового инструмента, например "GAZP" для акций Газпрома.
    board : str, optional
        Идентификатор, указывающий на специфическую торговую площадку или сегмент рынка.
        Если не указано, автоматически определятся первичный идентификатор на основе общих правил.
    """

    def resolve(secid: str, boardid: str | None) -> tuple[str, str, str, int, bool]:
        with Session() as client:
            data = client.get_objects(
                f"securities/{secid}",
                lambda data: [dict(zip(data["boards"]["columns"], row)) for row in data["boards"]["data"]],
            )
        if found := [
            item
            for item in data
            if item["secid"] == secid and (item["boardid"] == boardid if boardid is not None else item["is_primary"])
        ]:
            match found[0]:
                case {"boardid": boardid, "market": market, "decimals": decimals, "listed_till": listed_till}:
                    return market, boardid, secid, decimals, date.fromisoformat(listed_till) < date.today()
        raise LookupError(f"Unrecognized ticker' name '{secid}'")

    market, boardid, secid, decimals, delisted = resolve(name.upper(), board.upper() if board is not None else None)
    market = Market(market, boardid)
    return getattr(sys.modules[market.__module__], "Ticker")(market, boardid, secid, decimals, delisted)
