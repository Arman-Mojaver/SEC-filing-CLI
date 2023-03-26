import click

from more_itertools import chunked

from classes import CIKLoader, Entity, Base, Multiprocessor

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
@click.argument('ciks', type=str, nargs=-1, required=False)
@click.option('-f', '--form', type=click.Choice(FORM_TYPES), default='10-K')
@click.option('-u', '--user', type=str, default=None)
@click.option('-w', '--workers', type=int, default=10)
@click.option('-c', '--chunk_size', type=int, default=10)
def main(ciks: str, form: str, user: str, workers: int, chunk_size: int) -> None:
    if not ciks:
        ciks = CIKLoader().load().values()

    if not ciks:
        raise click.ClickException('Introduce a cik number or add a entities.json file to the running directory')

    if chunk_size > 10:
        click.confirm(
            f'Can the user you are making the requests with make more than 10 requests per second?', abort=True
        )

    entities = [Entity(cik=cik, form=form, user=user) for cik in ciks]

    for entity in entities:
        entity.run()

    all_filings = [filing for entity in entities for filing in entity.filings]
    chunked_filings = list(chunked(all_filings, n=chunk_size))

    if user:
        users = [user for _ in range(1, len(chunked_filings) + 1)]
        user_message = f'Running requests from user "{user}":'
    else:
        users = [f'{i}@'.join(Base.HEADERS["User-Agent"].split('@')) for i in range(1, len(chunked_filings) + 1)]
        user_message = f'Running requests from user/s : {", ".join(map(str, users))}'

    click.echo(user_message)

    for index, (chunk, user) in enumerate(zip(chunked_filings, users), 1):
        click.echo(f'\tRunning request batch {index}/{len(chunked_filings)}')

        filings = [filing for filing in chunk]
        processes = Multiprocessor(objects=filings, user=user, workers=workers)
        processes.run()

    click.echo('Done!')


if __name__ == '__main__':
    main()
