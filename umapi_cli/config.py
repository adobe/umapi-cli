import toml
from pathlib import Path

_BASEDIR = Path.cwd()


def exists(console_name):
    return (_BASEDIR / '.config' / console_name).exists()


def init(console_name, org_id, tech_acct, api_key, client_secret, priv_key_file, delete_key_file):
    config_dir = _BASEDIR / '.config'
    if not config_dir.exists():
        Path.mkdir(config_dir)
    priv_key_path = Path(priv_key_file)
    if not priv_key_path.exists():
        raise FileNotFoundError("Can't find private key file {}".format(priv_key_file))
    priv_key = priv_key_path.open('r').read()
    config_filename = config_dir / console_name
    with config_filename.open('w') as fh:
        toml.dump({
            'org_id': org_id,
            'tech_acct_id': tech_acct,
            'api_key': api_key,
            'client_secret': client_secret,
            'private_key_data': priv_key,
        }, fh)
    if delete_key_file:
        priv_key_path.unlink()
    return config_filename


def read(console_name):
    config_filename = _BASEDIR / '.config' / console_name
    if not config_filename.exists():
        raise FileNotFoundError("Can't find config file {} for '{}'".format(config_filename, console_name))
    with config_filename.open('r') as fh:
        return toml.load(fh)
