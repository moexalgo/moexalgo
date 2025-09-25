import csv
import typing as t
import zipfile
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO, TextIOWrapper

from moexalgo.utils import pd


@dataclass
class FileInfo:
    id: int
    dataset: str
    file_size: int
    filename: str
    uploaded_at: datetime
    year_month: str


class FileList(t.List[FileInfo]):

    @property
    def df(self) -> pd.DataFrame:
        """ Dataframe representation of this object. """
        return pd.DataFrame(self)

    def _repr_html_(self):
        return self.df._repr_html_()


class FileContent(t.List[str]):

    @property
    def df(self) -> pd.DataFrame:
        """ Dataframe representation of this object. """
        return pd.DataFrame(dict(csv=self))

    def _repr_html_(self):
        return self.df._repr_html_()


class FileData(t.List[t.Dict]):

    @property
    def df(self) -> pd.DataFrame:
        """ Dataframe representation of this object. """
        return pd.DataFrame(self)

    def _repr_html_(self):
        return self.df._repr_html_()


@dataclass
class DownloadInfo:
    download_url: str
    file_id: int
    filename: str
    success: bool


class File:

    def __init__(self, content: bytes):
        self.__data = None
        self._stream = BytesIO(content)
        with zipfile.ZipFile(self._stream, 'r') as zip_file:
            self.__content = [name for name in zip_file.namelist() if name.endswith('.csv')]
        self._stream.seek(0)

    def __iter__(self):
        return iter(self._data)

    @property
    def df(self) -> pd.DataFrame:
        """ Dataframe representation of this object. """
        return self._data.df

    @property
    def _data(self) -> FileData:
        if self.__data is None:
            self.__data = self._select(self._content[0])
        return self.__data

    @property
    def _content(self) -> FileContent:
        if not self.__content:
            raise ValueError('No csv files found in zip file')
        return FileContent(self.__content)

    def _select(self, csv_file: str) -> FileData:
        with zipfile.ZipFile(self._stream, 'r') as zip_file:
            with zip_file.open(csv_file) as file:
                text_file = TextIOWrapper(file, encoding='utf-8')
                reader = csv.DictReader(text_file)
                return FileData(row for row in reader)
