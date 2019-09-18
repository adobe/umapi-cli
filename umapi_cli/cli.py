import click
import sys
import umapi_client
from . import config
from . import client
from . import formatter


def _formatter(output_format, handler):
    fmtr_class = getattr(formatter, output_format, None)
    if fmtr_class is None:
        click.echo("Unknown format '{}'".format(output_format))
        sys.exit(1)
    return fmtr_class(handler)


def _output_handler(out_file=None):
    if out_file is not None:
        return open(out_file, 'w', encoding='utf-8')
    return sys.stdout


@click.group()
@click.help_option('-h', '--help')
def app():
    pass


@app.command()
@click.help_option('-h', '--help')
@click.option('--org-id', help="Organization ID",
              prompt='Organization ID')
@click.option('--tech-acct', help="Tech Account ID",
              prompt='Tech Account ID')
@click.option('--api-key', help="API Key",
              prompt='API Key')
@click.option('--client-secret', help="Client Secret",
              prompt='Client Secret')
@click.option('--priv-key', help="Private Key Path",
              prompt='Private Key Path', default='private.key')
@click.option('-d/-D', 'delete_key', help="Delete private key file (or do not delete it)",
              prompt='Delete private key file?', default=False)
@click.option('-c', '--console-name', help='Short name to assign to the integration config',
              default='main', show_default=True)
@click.option('-o', 'overwrite', help="Overwrite existing config",
              default=False)
def init(org_id, tech_acct, api_key, client_secret, priv_key, delete_key, console_name, overwrite):
    """Initialize a new UMAPI client config"""
    if config.exists(console_name):
        confirm_overwrite = overwrite or click.confirm(
            "Overwrite config for '{}'?".format(console_name), default=False)
        if not confirm_overwrite:
            click.echo("Can't overwrite config for '{}'".format(console_name))
            sys.exit(1)

    config_filename = config.init(console_name, org_id, tech_acct, api_key, client_secret, priv_key, delete_key)
    click.echo("'{}' initialized at {}".format(console_name, config_filename))


@app.command()
@click.help_option('-h', '--help')
@click.option('-c', '--console-name', help='Short name to assign to the integration config',
              default='main', show_default=True)
@click.option('-f', '--format', 'output_format', help='Output format', metavar='csv|json|pretty', default='pretty',
              show_default=True)
@click.option('-e', '--email', help='User email address', required=True)
def user_read(console_name, output_format, email):
    """Get details for a single user"""
    fmtr = _formatter(output_format, _output_handler())
    auth_config = config.read(console_name)
    umapi_conn = client.create_conn(auth_config, False)
    user = umapi_client.UserQuery(umapi_conn, email).result()
    if not user:
        click.echo('No user found')
        sys.exit(1)
    fmtr.record(user)
    fmtr.write()


@app.command()
@click.help_option('-h', '--help')
@click.option('-c', '--console-name', help='Short name to assign to the integration config',
              default='main', show_default=True)
@click.option('-f', '--format', 'output_format', help='Output format', metavar='csv|json|pretty', default='pretty',
              show_default=True)
@click.option('-o', '--out-file', help='Write output to this filename', metavar='FILENAME')
def user_read_all(console_name, output_format, out_file):
    """Get details for all users belonging to a console"""
    fmtr = _formatter(output_format, _output_handler(out_file))
    auth_config = config.read(console_name)
    umapi_conn = client.create_conn(auth_config, False)
    query = umapi_client.UsersQuery(umapi_conn)
    for user in query:
        fmtr.record(user)
    fmtr.write()


@app.command()
@click.help_option('-h', '--help')
@click.option('-c', '--console-name', help='Short name to assign to the integration config',
              default='main', show_default=True)
@click.option('-f', '--format', 'output_format', help='Output format', metavar='csv|json|pretty', default='pretty',
              show_default=True)
@click.option('-g', '--group', 'group_name', help='Group name', required=True)
def group_read(console_name, output_format, group_name):
    """Get details for a single user group"""
    fmtr = _formatter(output_format, _output_handler())
    auth_config = config.read(console_name)
    umapi_conn = client.create_conn(auth_config, False)
    query = umapi_client.GroupsQuery(umapi_conn)
    group,  = [g for g in query if g['groupName'].lower() == group_name.lower()]
    fmtr.record(group)
    fmtr.write()


@app.command()
@click.help_option('-h', '--help')
@click.option('-c', '--console-name', help='Short name to assign to the integration config',
              default='main', show_default=True)
@click.option('-f', '--format', 'output_format', help='Output format', metavar='csv|json|pretty', default='pretty',
              show_default=True)
@click.option('-o', '--out-file', help='Write output to this filename', metavar='FILENAME')
def group_read_all(console_name, output_format, out_file):
    """Get details for all groups in a console"""
    fmtr = _formatter(output_format, _output_handler(out_file))
    auth_config = config.read(console_name)
    umapi_conn = client.create_conn(auth_config, False)
    query = umapi_client.GroupsQuery(umapi_conn)
    for group in query:
        fmtr.record(group)
    fmtr.write()


@app.command()
@click.help_option('-h', '--help')
@click.option('-c', '--console-name', help='Short name to assign to the integration config',
              default='main', show_default=True)
@click.option('--type', 'user_type', help="User's identity type", metavar='adobeID|enterpriseID|federatedID',
              default='federatedID', show_default=True)
@click.option('--email', help="User's email address", required=True)
@click.option('--username', help="User's username (set to email if omitted)")
@click.option('--domain', help="User's directory domain (set to username domain if omitted, if username is an "
                               "email, this must be set to same domain)")
@click.option('--groups', help="Comma-delimited list of groups to assign user")
@click.option('--firstname', help="User's first name")
@click.option('--lastname', help="User's last name")
@click.option('--country', help="User's two-letter (ISO-3166-1 alpha2) country code", required=True)
@click.option('-t', '--test', 'test_mode', help="Run command in test mode", default=False, show_default=False,
              is_flag=True)
def user_create(console_name, user_type, email, username, domain, groups, firstname, lastname, country, test_mode):
    auth_config = config.read(console_name)
    umapi_conn = client.create_conn(auth_config, test_mode)
    user = client.user_create_action(user_type, email, username, domain, groups, firstname, lastname, country)
    umapi_conn.execute_single(user)
    umapi_conn.execute_queued()
    click.echo("errors: {}".format(user.execution_errors()))
