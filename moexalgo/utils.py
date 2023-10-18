import decimal
import json as _json
from datetime import datetime, date, time


class RequiredImport:

    def __init__(self, name):
        self.__name = name

    def __getattr__(self, item):
        raise ImportError(f'Required `{self.__name}`')


try:
    import pandas
except ImportError:
    pandas = RequiredImport('pandas')


def is_interactive():
    """ Возвращает `True` если код исполняется в интерактивном режиме, например в jupiter notebook
    """
    import __main__ as main
    return not hasattr(main, '__file__')


class json:
    """ Расширение JSON енкодера
    """
    loads = _json.loads
    JSONDecodeError = _json.JSONDecodeError

    @staticmethod
    def dumps(*args, **kwargs):
        """

        Parameters
        ----------
        args
        kwargs

        Returns
        -------

        """

        def default(obj):
            """

            Parameters
            ----------
            obj

            Returns
            -------

            """
            if isinstance(obj, decimal.Decimal):
                return float(str(obj))
            elif isinstance(obj, (datetime, date, time)):
                return obj.isoformat()
            raise TypeError

        return _json.dumps(*args, **kwargs, default=default)


def result_deserializer(data: dict, *sections, key=None):
    """

    Parameters
    ----------
    data
    sections
    key

    Returns
    -------

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


def item_normalizer(metadata, item):
    """

    Parameters
    ----------
    metadata
    item

    Returns
    -------

    """
    conv = {'int32': lambda s: int(s) if s is not None else None,
            'int64': lambda s: int(s) if s is not None else None,
            'double': lambda s: float(s) if s is not None else None,
            'date': lambda s: date.fromisoformat(s.strip()) if s is not None and s != '0000-00-00' else None,
            'datetime': lambda s: datetime.fromisoformat(s.strip()) if s is not None else None,
            'time': lambda s: time.fromisoformat(s.strip()) if s is not None else None}
    return dict((key, conv.get(metadata[key]['type'], str)(value)) for key, value in item.items())
