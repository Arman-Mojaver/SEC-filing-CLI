import time
import click

from more_itertools import chunked

from classes import CIKLoader, Entity


@click.command()
def main():
    ciks = CIKLoader().load()

    entities = [Entity(cik=cik) for cik in ciks]

    for entity in entities:
        entity.run()

    all_filings = [filing for entity in entities for filing in entity.filings]
    chunked_filings = list(chunked(all_filings, n=10))

    for index, chunk in enumerate(chunked_filings, 1):
        click.echo(f'Running request batch {index}/{len(chunked_filings)}')
        for filing in chunk:
            filing.run()
        time.sleep(1)

    click.echo('Done!')


if __name__ == '__main__':
    main()
