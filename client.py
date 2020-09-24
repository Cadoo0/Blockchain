from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend
import click
from os import makedirs, getcwd, path


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


cli.add_command(create_client)


if __name__ == '__main__':
    cli()