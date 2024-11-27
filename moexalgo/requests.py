import typing as t

from moexalgo.session import Session, AUTH_CERT
from moexalgo.utils import result_deserializer


def _get_sections(path: str, *sections: str,
                  session=None, **options: dict) -> t.Optional[t.Iterator[dict]]:
    with Session(session or Session(auth_cert=AUTH_CERT)) as client:
        items = client.get_objects(path, lambda data: result_deserializer(data, *sections), **options)
        return items


def get_secid_info_and_boards(secid: int) -> tuple[dict[str, t.Any], dict[str, t.Any]]:
    with Session(Session(auth_cert=AUTH_CERT)) as client:
        sections = client.get_objects(f'securities/{secid}',
                                      lambda data: result_deserializer(data, 'description', 'boards'))
        return (
            dict((item.pop('name'), item) for item in sections['description']),
            dict((item.get('boardid'), item) for item in sections['boards'])
        )
