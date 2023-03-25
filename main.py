import time

from more_itertools import chunked

from classes import CIKLoader, Entity


ciks = CIKLoader().load()
entities = [Entity(cik=cik) for cik in ciks]

for entity in entities:
    entity.run()

all_filings = [filing for entity in entities for filing in entity.filings]
chunked_filings = chunked(all_filings, n=10)

for chunk in chunked_filings:
    for filing in chunk:
        filing.run()
    time.sleep(1)
