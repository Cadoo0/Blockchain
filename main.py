from hashlib import sha256
from json import dumps, dump, load
from time import time
import click


class Blockchain:

    difficulty = 4

    def __init__(self, pending_transactions, blocks):
        self.pending_transactions = pending_transactions
        self.blocks = blocks

    def create_first_block(self):
        block = Block(0, [], time(), '0')
        self.calculate_proof_of_work(block)
        self.blocks.append(block)

    @property
    def last_block(self):
        return self.blocks[-1]

    def add_pending_transaction(self, transaction):
        self.pending_transactions.append(transaction)

    def is_valid_proof_of_work(self, block, block_hash):
        return block_hash.startswith('0' * self.difficulty) and block_hash == block.hash()

    def calculate_proof_of_work(self, block):
        calculated_hash = block.hash()

        while not calculated_hash.startswith('0' * self.difficulty):
            block.nonce += 1
            calculated_hash = block.hash()

        return calculated_hash

    def create_block(self):

        if len(self.pending_transactions) == 0:
            raise Exception("Cannot create a block if there are no pending transactions")

        last_block = self.last_block

        block = Block(last_block.index + 1, self.pending_transactions, time(), last_block.hash())

        proof = self.calculate_proof_of_work(block)

        if not self.is_valid_proof_of_work(block, proof):
            raise Exception("The given proof of work is not valid")

        block.hash = proof
        self.blocks.append(block)
        self.pending_transactions = []

        return block

    @property
    def __dict__(self):
        return {
            'pending_transactions': [transaction.__dict__ for transaction in self.pending_transactions],
            'blocks': [block.__dict__ for block in self.blocks]
        }

    def save_to_disk(self):
        with open('chain.json', 'w') as target_file:
            dump(self.__dict__, target_file)

    def load_from_disk(self):
        with open('chain.json', 'r') as target_file:
            data = load(target_file)

            for pending_transaction in data['pending_transactions']:
                pending_transaction = Transaction(pending_transaction['sender'], pending_transaction['receiver'], float(pending_transaction['amount']))
                self.pending_transactions.append(pending_transaction)

            for block in data['blocks']:
                transactions = []

                for transaction in block['transactions']:
                    transactions.append(Transaction(transaction['sender'], transaction['receiver'], float(transaction['amount'])))

                block = Block(block['index'], transactions, block['timestamp'], block['previous_hash'], block['nonce'])
                self.blocks.append(block)


class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce

    def hash(self):
        json_string = dumps(self.__dict__).encode()
        return sha256(json_string).hexdigest()

    @property
    def __dict__(self):
        return {
            'index': self.index,
            'transactions': [transaction.__dict__ for transaction in self.transactions],
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
        }


class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount


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
def add_pending_transaction(sender, receiver, amount):
    chain = Blockchain([], [])
    chain.load_from_disk()
    transaction = Transaction(sender, receiver, amount)
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
            return

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
        click.echo('Integrity problem at block ' + str(x))
        return

    if previous_block.hash() != current_block.previous_hash:
        click.echo('Integrity problem at block ' + str(x))
        return

    click.echo('No integrity problems found')


cli.add_command(reset)
cli.add_command(add_pending_transaction)
cli.add_command(create_block)
cli.add_command(verify_integrity)
cli.add_command(verify_integrity_of_block)


if __name__ == '__main__':
    cli()