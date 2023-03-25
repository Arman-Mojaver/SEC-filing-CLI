import requests
import json


class Entity(object):
    USER = "arman@mojaver.com"
    HEADER = {"User-Agent": USER}

    def __init__(self, cik):
        self.cik = cik
        self.url = f'https://data.sec.gov/submissions/CIK{self.cik}.json'

        self.data = None

    def get_data(self):
        response = requests.get(self.url, headers={"User-Agent": self.USER})
        return json.loads(s=response.content.decode())

    def run(self):
        self.data = self.get_data()


entity = Entity(cik='0000320193')
entity.run()
print(entity.data)
