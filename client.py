from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import click
from os import makedirs, getcwd, path
import base64
import requests


def generate_public_private_combo():
    key = rsa.generate_private_key(
        backend=crypto_default_backend(),
        public_exponent=65537,
        key_size=2048
    )
    private_key = key.private_bytes(
        crypto_serialization.Encoding.PEM,
        crypto_serialization.PrivateFormat.PKCS8,
        crypto_serialization.NoEncryption()
    )
    public_key = key.public_key().public_bytes(
        crypto_serialization.Encoding.OpenSSH,
        crypto_serialization.PublicFormat.OpenSSH
    )

    return {
        'public': public_key,
        'private': private_key
    }


@click.group()
def cli():
    pass


@click.command()
@click.option('--name', help='Your name', prompt='Name')
def create_client(name):
    current_path = getcwd()
    clients_path = current_path + '/clients/'
    client_path = clients_path + '/' + name

    if path.isdir(client_path):
        click.echo('Client ' + name + ' already exists')
        return

    makedirs(client_path)

    keys = generate_public_private_combo()
    private_key = keys['private']
    public_key = keys['public']

    with open(client_path + '/public.pub', 'wb') as target_file:
        target_file.write(public_key)

    with open(client_path + '/private.pem', 'wb') as target_file:
        target_file.write(private_key)


@click.command()
@click.option('--sender', help='The person sending the money', prompt='Sender')
@click.option('--receiver', help='The person receiving the money', prompt='Receiver')
@click.option('--amount', help='The desired amount you want to send', prompt='Amount')
def create_transaction(sender, receiver, amount):
    current_path = getcwd()
    clients_path = current_path + '/clients/'
    client_path = clients_path + '/' + sender

    if not path.isdir(client_path):
        click.echo('Client ' + sender + ' does not exist')
        return

    with open(client_path + '/public.pub', 'rb') as public_file:
        public_key = serialization.load_ssh_public_key(
            public_file.read()
        )

    with open(client_path + '/private.pem', 'rb') as private_file:
        private_key = serialization.load_pem_private_key(
            private_file.read(),
            password=None
        )

    message = {
        'sender': sender,
        'receiver': receiver,
        'amount': amount,
    }

    payload = {
        'sender': sender,
        'receiver': receiver,
        'amount': amount,
        'message': str(message).encode('ascii'),
        'public_key': base64.b64encode(public_key.public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH
        )),
        'signature': base64.b64encode(private_key.sign(
            str(message).encode('ascii'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        ))
    }

    response = requests.post('http://127.0.0.1:5000/add-transaction', data=payload)

    print(response.content)


@click.command()
def create_block():
    response = requests.post('http://127.0.0.1:5000/create-block')
    print(response.content)


cli.add_command(create_client)
cli.add_command(create_transaction)
cli.add_command(create_block)


if __name__ == '__main__':
    cli()