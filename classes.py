import os
import requests
import json


class Base(object):
    HEADERS = {"User-Agent": "user@domain.com"}

    DATA_DIRECTORY_NAME = 'Data'
    CIKS_FILE_NAME = 'ciks.json'

    CWD = os.getcwd()
    DATA_DIRECTORY = os.path.join(CWD, DATA_DIRECTORY_NAME)
    CIKS_PATH = os.path.join(CWD, CIKS_FILE_NAME)

    @staticmethod
    def run_request(url, headers):
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

    def __init__(self, url, entity_directory, user=None):
        self.url = url
        self.entity_directory = entity_directory
        self.headers = {"User-Agent": user} if user else self.HEADERS

        self.filename = self.get_directory_filename(absolute_path=url)
        self.filepath = os.path.join(self.entity_directory, self.filename)

        self.data = None

    @staticmethod
    def get_directory_filename(absolute_path):
        file_name = os.path.basename(absolute_path)
        directory_name = os.path.basename(os.path.dirname(absolute_path))
        return f'{directory_name}-{file_name}'

    def dump(self):
        with open(self.filepath, 'w+') as file:
            file.write(self.data)

    def run(self):
        self.data = self.run_request(url=self.url, headers=self.headers)
        self.dump()


class Entity(Base):
    __repr_fields__ = ('url', 'cik',)

    def __init__(self, cik, form, user=None):
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
    def process_cik(cik):
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

    def create_data_directory(self):
        if os.path.isdir(self.DATA_DIRECTORY):
            return

        os.mkdir(self.DATA_DIRECTORY)

    def create_entity_directory(self):
        if os.path.isdir(self.entity_directory):
            return

        os.mkdir(self.entity_directory)

    def get_filing_urls(self):
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

    def get_filings(self):
        return [Filing(url=url, entity_directory=self.entity_directory) for url in self.filing_urls]

    def run(self):
        self.metadata = json.loads(s=self.run_request(url=self.url, headers=self.headers))

        self.name = self.metadata['name']
        self.entity_directory = os.path.join(self.DATA_DIRECTORY, self.name)
        self.create_entity_directory()

        self.filing_urls = self.get_filing_urls()
        self.filings = self.get_filings()


class CIKLoader(Base):
    def __init__(self):
        pass

    def load(self):
        if not os.path.isfile(self.CIKS_PATH):
            return

        with open(self.CIKS_PATH, 'r') as fp:
            return json.load(fp)