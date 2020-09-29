import click
from classes import Blockchain, Block, Transaction


@click.group()
def cli():
    pass


@click.command()
def reset():
    chain = Blockchain([], [])
    chain.create_first_block()
    chain.save_to_disk()


@click.command()
@click.option('--sender', help='The person who sent the money', prompt='Sender')
@click.option('--receiver', help='The person who received the money', prompt='Receiver')
@click.option('--amount', help='The amount of money in question', prompt='Amount')
@click.option('--public_key', help='Public key', prompt='Public Key')
@click.option('--signature', help='Signature', prompt='Signature')
def add_pending_transaction(sender, receiver, amount):
    chain = Blockchain([], [])
    chain.load_from_disk()
    transaction = Transaction(sender, receiver, amount, None, None)
    chain.add_pending_transaction(transaction)
    chain.save_to_disk()


@click.command()
def create_block():
    chain = Blockchain([], [])
    chain.load_from_disk()
    chain.create_block()
    chain.save_to_disk()


@click.command()
def verify_integrity():
    chain = Blockchain([], [])
    chain.load_from_disk()
    x = 0
    total_blocks = len(chain.blocks)
    while x < total_blocks:
        current_block = chain.blocks[x]

        if current_block.index == 0:
            x += 1
            continue

        previous_block = chain.blocks[x - 1]

        if not current_block.hash().startswith('0' * Blockchain.difficulty):
            click.echo('Integrity problem at block ' + str(x))
            return

        if (x + 1) == total_blocks:
            break

        if previous_block.hash() != current_block.previous_hash:
            click.echo('Integrity problem at block ' + str(x))
            return

        x += 1

    click.echo('No integrity problems found')


@click.command()
@click.option('--index', help='The block you want to check', prompt='Block index', type=click.INT)
def verify_integrity_of_block(index):
    chain = Blockchain([], [])
    chain.load_from_disk()

    if index == 0:
        click.echo('Cannot check the first block')
        return

    try:
        current_block = chain.blocks[index]
        previous_block = chain.blocks[index - 1]
    except IndexError:
        click.echo('Block index ' + str(index) + ' does not exist')
        return

    if not current_block.hash().startswith('0' * Blockchain.difficulty):
        click.echo('Integrity problem at block ' + str(index))
        return

    if previous_block.hash() != current_block.previous_hash:
        click.echo('Integrity problem at block ' + str(index))
        return

    click.echo('No integrity problems found')


cli.add_command(reset)
cli.add_command(add_pending_transaction)
cli.add_command(create_block)
cli.add_command(verify_integrity)
cli.add_command(verify_integrity_of_block)


if __name__ == '__main__':
    cli()
