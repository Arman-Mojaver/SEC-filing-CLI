import os
import requests
import json


class Entity(object):
    USER = "arman@mojaver.com"
    HEADER = {"User-Agent": USER}

    DATA_DIRECTORY_NAME = 'Data'
    DATA_DIRECTORY = os.path.join(os.getcwd(), DATA_DIRECTORY_NAME)

    def __init__(self, cik):
        self.cik = self.process_cik(cik=cik)
        self.url = f'https://data.sec.gov/submissions/CIK{self.cik}.json'
        self.cik_directory = os.path.join(self.DATA_DIRECTORY, self.cik)

        self.create_data_directory()
        self.create_cik_directory()

        self.metadata = None

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

    def run(self):
        self.metadata = self.get_metadata()


class CIKLoader(object):
    CIKS_FILE_NAME = 'ciks.json'
    CIKS_PATH = os.path.join(os.getcwd(), CIKS_FILE_NAME)

    def __init__(self):
        pass

    def load(self):
        with open(self.CIKS_PATH, 'r') as fp:
            return json.load(fp)


ciks = CIKLoader().load()

for cik in ciks:
    entity = Entity(cik=cik)
    entity.run()
