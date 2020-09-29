from hashlib import sha256
from json import dumps, dump, load
from time import time

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
                pending_transaction = Transaction(
                    pending_transaction['sender'],
                    pending_transaction['receiver'],
                    float(pending_transaction['amount']),
                    pending_transaction['public_key'],
                    pending_transaction['signature'])
                self.pending_transactions.append(pending_transaction)

            for block in data['blocks']:
                transactions = []

                for transaction in block['transactions']:
                    transactions.append(Transaction(
                        transaction['sender'],
                        transaction['receiver'],
                        float(transaction['amount']),
                        transaction['public_key'],
                        transaction['signature']))

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
    def __init__(self, sender, receiver, amount, public_key, signature):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.public_key = public_key
        self.signature = signature
