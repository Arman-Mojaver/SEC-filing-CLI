import os
import requests
import json


class Base(object):
    USER = "arman@mojaver.com"
    HEADER = {"User-Agent": USER}

    DATA_DIRECTORY_NAME = 'Data'
    CIKS_FILE_NAME = 'ciks.json'

    CWD = os.getcwd()
    DATA_DIRECTORY = os.path.join(CWD, DATA_DIRECTORY_NAME)
    CIKS_PATH = os.path.join(CWD, CIKS_FILE_NAME)

    def __repr__(self) -> str:
        fields = getattr(self, '__repr_fields__', tuple())

        attributes = []
        for key in fields:
            attributes.append('%s=%r' % (key, getattr(self, key, None)))
        return '<%s(%s)>' % (self.__class__.__name__, ', '.join(attributes))


class Filing(Base):
    __repr_fields__ = ('url',)

    def __init__(self, url, cik, cik_directory):
        self.url = url
        self.cik = cik
        self.cik_directory = cik_directory

        self.filename = self.get_directory_filename(absolute_path=url)
        self.filepath = os.path.join(self.cik_directory, self.filename)

        self.data = None

    @staticmethod
    def get_directory_filename(absolute_path):
        file_name = os.path.basename(absolute_path)
        directory_name = os.path.basename(os.path.dirname(absolute_path))
        return f'{directory_name}-{file_name}'

    def get_data(self):
        response = requests.get(self.url, headers={"User-Agent": self.USER})

        if response.status_code == 404:
            raise ValueError(f'Invalid url: {self.url}')

        if response.status_code == 403:
            raise ValueError(f'Permission denied: Introduce correct headers: {self.HEADER}')

        return response.content.decode()

    def dump(self):
        with open(self.filepath, 'w+') as file:
            file.write(self.data)

    def run(self):
        self.data = self.get_data()
        self.dump()


class Entity(Base):
    __repr_fields__ = ('url', 'cik',)

    TEN_K_KEY = '10-K'

    def __init__(self, cik):
        self.cik = self.process_cik(cik=cik)
        self.url = f'https://data.sec.gov/submissions/CIK{self.cik}.json'
        self.cik_directory = os.path.join(self.DATA_DIRECTORY, self.cik)

        self.create_data_directory()
        self.create_cik_directory()

        self.metadata = None
        self.filing_urls = None
        self.filings = None

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

    def create_cik_directory(self):
        if os.path.isdir(self.cik_directory):
            return

        os.mkdir(self.cik_directory)

    def get_metadata(self):
        response = requests.get(self.url, headers={"User-Agent": self.USER})

        if response.status_code == 404:
            raise ValueError(f'Invalid url: {self.url}')

        if response.status_code == 403:
            raise ValueError(f'Permission denied: Introduce correct headers: {self.HEADER}')

        return json.loads(s=response.content.decode())

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
            if form == self.TEN_K_KEY
        ]

    def get_filings(self):
        return [Filing(url=url, cik=self.cik, cik_directory=self.cik_directory) for url in self.filing_urls]

    def run(self):
        self.metadata = self.get_metadata()
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