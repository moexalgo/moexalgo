from moexalgo import session
from moexalgo.ahdata.client import Client
from moexalgo.ahdata.models import FileInfo, FileList, File
from moexalgo.session import HasOptions, Session

URL = 'https://ahdata.ru'


def files(dataset: str = None) -> FileList:
    path = f"/api/files/{dataset}" if dataset else f"/api/files"
    with Session(HasOptions(base_url=URL), client_cls=Client) as client:
        data = client.get(path)
        return FileList(FileInfo(dataset=dataset, **item)
                        if dataset else FileInfo(**item) for item in data['files'])


def download(dataset: str, period: str):
    params = {
        'dataset_path': dataset,
        'year_month': period,
        'jwt_token': session.TOKEN
    }
    with Session(HasOptions(base_url=URL), client_cls=Client) as client:
        data = client.get('/download', **params)
        return File(data)
