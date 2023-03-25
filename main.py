import time
import click

from more_itertools import chunked

from classes import CIKLoader, Entity


@click.command()
@click.argument('ciks', type=str, nargs=-1)
def main(ciks):
    if not ciks:
        ciks = CIKLoader().load()

    if not ciks:
        raise click.ClickException('Introduce a cik number or add a ciks.json file to the running directory')

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
