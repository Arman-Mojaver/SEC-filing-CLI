import requests
import json


class Entity(object):
    USER = "arman@mojaver.com"
    HEADER = {"User-Agent": USER}

    def __init__(self, cik):
        self.cik = self.process_cik(cik=cik)
        self.url = f'https://data.sec.gov/submissions/CIK{self.cik}.json'

        self.data = None

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

    def get_data(self):
        response = requests.get(self.url, headers={"User-Agent": self.USER})
        return json.loads(s=response.content.decode())

    def run(self):
        self.data = self.get_data()


entity = Entity(cik='320193')
entity.run()
print(entity.data)
