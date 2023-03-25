import time
import click

from more_itertools import chunked

from classes import CIKLoader, Entity


FORM_TYPES = [
    '10-K',
    '10-Q',
    '25',
    '25-NSE',
    '3',
    '3/A',
    '4',
    '4/A',
    '424B2',
    '8-A12B',
    '8-K',
    '8-K/A',
    'CERT',
    'CERTNYS',
    'CORRESP',
    'DEF 14A',
    'DEFA14A',
    'DFAN14A',
    'FWP',
    'IRANNOTICE',
    'NO ACT',
    'PRE 14A',
    'PX14A6G',
    'PX14A6N',
    'S-3ASR',
    'S-8',
    'S-8 POS',
    'SC 13G',
    'SC 13G/A',
    'SD',
    'UPLOAD',
]


@click.command()
@click.argument('ciks', type=str, nargs=-1)
@click.option('-f', '--form', type=click.Choice(FORM_TYPES), default='10-K')
def main(ciks, form):
    if not ciks:
        ciks = CIKLoader().load()

    if not ciks:
        raise click.ClickException('Introduce a cik number or add a ciks.json file to the running directory')

    entities = [Entity(cik=cik, form=form) for cik in ciks]

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
