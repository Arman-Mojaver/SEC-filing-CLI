import os
import requests
import json

from typing import Union, List, Any, Optional

from concurrent.futures import ThreadPoolExecutor


class Base(object):
    HEADERS = {"User-Agent": "user@domain.com"}

    DATA_DIRECTORY_NAME = 'Data'
    CIKS_FILE_NAME = 'entities.json'

    CWD = os.getcwd()
    DATA_DIRECTORY = os.path.join(CWD, DATA_DIRECTORY_NAME)
    CIKS_PATH = os.path.join(CWD, CIKS_FILE_NAME)

    @staticmethod
    def run_request(url: str, headers: dict) -> str:
        response = requests.get(url, headers=headers)

        if response.status_code == 404:
            raise ValueError(f'Invalid url: {url}')

        if response.status_code == 403:
            raise ValueError(f'Permission denied: Introduce correct headers: {headers}')

        return response.content.decode()

    def __repr__(self) -> str:
        fields = getattr(self, '__repr_fields__', tuple())

        attributes = []
        for key in fields:
            attributes.append('%s=%r' % (key, getattr(self, key, None)))
        return '<%s(%s)>' % (self.__class__.__name__, ', '.join(attributes))


class Filing(Base):
    __repr_fields__ = ('url',)

    def __init__(self, url: str, entity_directory: str, user: str = None) -> None:
        self.url = url
        self.entity_directory = entity_directory
        self.headers = {"User-Agent": user} if user else self.HEADERS

        self.filename = self.get_directory_filename(absolute_path=url)
        self.filepath = os.path.join(self.entity_directory, self.filename)

        self.data = None

    @staticmethod
    def get_directory_filename(absolute_path: str) -> str:
        file_name = os.path.basename(absolute_path)
        directory_name = os.path.basename(os.path.dirname(absolute_path))
        return f'{directory_name}-{file_name}'

    def dump(self) -> None:
        with open(self.filepath, 'w+') as file:
            file.write(self.data)

    def run(self, user: str) -> None:
        headers = self.headers
        if user:
            headers = {"User-Agent": user}

        self.data = self.run_request(url=self.url, headers=headers)
        self.dump()


class Entity(Base):
    __repr_fields__ = ('cik', 'form', 'user',)

    def __init__(self, cik: Union[str, int], form: str, user: str = None) -> None:
        self.cik = self.process_cik(cik=cik)
        self.form = form
        self.headers = {"User-Agent": user} if user else self.HEADERS

        self.url = f'https://data.sec.gov/submissions/CIK{self.cik}.json'
        self.create_data_directory()

        self.entity_directory = None
        self.metadata = None
        self.filing_urls = None
        self.filings = None
        self.name = None

    @staticmethod
    def process_cik(cik: Union[str, int]) -> str:
        if not isinstance(cik, (str, int)):
            raise TypeError(f'Invalid cik. Valid types are <str, int>. Introduced type: {type(cik)}')

        if isinstance(cik, int):
            cik = str(cik)

        if len(cik) == 10:
            return cik
        elif len(cik) > 10:
            raise ValueError(f'Invalid cik length (max 10): {cik}')
        else:
            zeros = ''.join(['0' for _ in range(10 - len(cik))])
            return zeros + cik

    def create_data_directory(self) -> None:
        if os.path.isdir(self.DATA_DIRECTORY):
            return

        os.mkdir(self.DATA_DIRECTORY)

    def create_entity_directory(self) -> None:
        if os.path.isdir(self.entity_directory):
            return

        os.mkdir(self.entity_directory)

    def get_filing_urls(self) -> List[str]:
        filings = self.metadata.get('filings').get('recent')

        if not filings:
            raise ValueError(f'Filings not found in response')

        list_length = len(filings.get('form'))
        for list_ in filings.values():
            if len(list_) != list_length:
                raise ValueError(
                    f'There is a mismatch in the metadata structure of the filing. {len(list_)} != {list_length}'
                )

        return [
            f'https://www.sec.gov/Archives/edgar/data/{self.cik}/{accession_number.replace("-", "")}/{primary_document}'
            for form, accession_number, primary_document in zip(
                filings['form'], filings['accessionNumber'], filings['primaryDocument']
            )
            if form == self.form
        ]

    def get_filings(self) -> List['Filing']:
        return [Filing(url=url, entity_directory=self.entity_directory) for url in self.filing_urls]

    def run(self) -> None:
        self.metadata = json.loads(s=self.run_request(url=self.url, headers=self.headers))

        self.name = self.metadata['name']
        self.entity_directory = os.path.join(self.DATA_DIRECTORY, self.name)
        self.create_entity_directory()

        self.filing_urls = self.get_filing_urls()
        self.filings = self.get_filings()


class CIKLoader(Base):
    def __init__(self) -> None:
        pass

    def load(self) -> Optional[dict]:
        if not os.path.isfile(self.CIKS_PATH):
            return None

        with open(self.CIKS_PATH, 'r') as fp:
            return json.load(fp)


class Multiprocessor:
    def __init__(self, objects: List[Any], user: str, workers: int = 10) -> None:
        self.objects = objects
        self.user = user
        self.workers = workers

    @staticmethod
    def mapper(obj: Any, user: str) -> None:
        return obj.run(user=user)

    def run(self) -> None:
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            for obj in self.objects:
                executor.submit(self.mapper, obj, user=self.user)
