from cryptography.exceptions import InvalidSignature
from flask import Flask, request
from classes import Blockchain, Block, Transaction
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import base64

app = Flask(__name__)


@app.route('/add-transaction', methods=['POST'])
def add_transaction():
    blockchain = Blockchain([], [])
    blockchain.load_from_disk()
    data = request.form
    sender = data['sender']
    receiver = data['receiver']
    amount = data['amount']
    message = data['message'].encode('ascii')
    public_key = serialization.load_ssh_public_key(data=base64.b64decode(data['public_key']))
    signature = base64.b64decode(data['signature'])

    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
    except InvalidSignature:
        return 'Invalid signature'

    transaction = Transaction(sender, receiver, float(amount), data['public_key'], data['signature'])
    blockchain.add_pending_transaction(transaction)
    blockchain.save_to_disk()

    return 'Success'


@app.route('/create-block', methods=['POST'])
def create_block():
    chain = Blockchain([], [])
    chain.load_from_disk()
    try:
        chain.create_block()
    except:
        pass
    chain.save_to_disk()
    return 'Success'
