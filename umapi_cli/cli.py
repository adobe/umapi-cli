import click
import sys
import umapi_client
import dotenv
from pathlib import Path
from . import config
from . import client
from . import formatter
from .action_queue import ActionQueue
from .formatter import normalize
from . import log
from .version import __version__ as app_version

def _formatter(output_format, handler, record_type):
    fmtr_class = getattr(formatter, output_format, None)
    if fmtr_class is None:
        click.echo("Unknown format '{}'".format(output_format))
        sys.exit(1)
    return fmtr_class(handler, record_type)


def _output_handler(out_file=None):
    if out_file is not None:
        return open(out_file, 'w', encoding='utf-8')
    return sys.stdout


def _input_handler(in_file):
    return open(in_file, 'r')


@click.group()
@click.option('--env', 'env_file', help="Path to .env file (optional)", default=None, type=click.Path())
@click.option('-t', '--test', 'test_mode', help="Run command in test mode", default=False, show_default=False,
              is_flag=True)
@click.option('-v', count=True)
@click.help_option('-h', '--help')
@click.version_option(app_version, '--version', message='%(prog)s %(version)s')
@click.pass_context
def app(ctx, env_file, test_mode, v):
    log.init(v)
    if env_file is not None:
        dotenv.load_dotenv(env_file)
    else:
        dotenv.load_dotenv()
    ctx.ensure_object(dict)
    conf = config.get_options()
    ctx.obj['conn'] = client.create_conn(conf, test_mode)


@app.command()
@click.help_option('-h', '--help')
@click.option('-f', '--format', 'output_format', help='Output format', metavar='csv|json|pretty', default='pretty',
              show_default=True)
@click.option('-e', '--email', help='User email address', required=True)
@click.pass_context
def user_read(ctx, output_format, email):
    """Get details for a single user"""
    fmtr = _formatter(output_format, _output_handler(), 'user')
    umapi_conn = ctx.obj['conn']
    user = umapi_client.UserQuery(umapi_conn, email).result()
    if not user:
        click.echo('No user found')
        sys.exit(1)
    fmtr.record(user)
    fmtr.write()


@app.command()
@click.help_option('-h', '--help')
@click.option('-f', '--format', 'output_format', help='Output format', metavar='csv|json|pretty', default='pretty',
              show_default=True)
@click.option('-o', '--out-file', help='Write output to this filename', metavar='FILENAME')
@click.pass_context
def user_read_all(ctx, output_format, out_file):
    """Get details for all users belonging to a console"""

    fmtr = _formatter(output_format, _output_handler(out_file), 'user')
    umapi_conn = ctx.obj['conn']
    query = umapi_client.UsersQuery(umapi_conn)
    report_total = True
    for user in query:
        total, *_ = query.stats()
        if total is not None and report_total:
            log.info(f"Total records: {total}")
            report_total = False
        fmtr.record(user)
    fmtr.write()


@app.command()
@click.help_option('-h', '--help')
@click.option('-f', '--format', 'output_format', help='Output format', metavar='csv|json|pretty', default='pretty',
              show_default=True)
@click.option('-g', '--group', 'group_name', help='Group name', required=True)
@click.pass_context
def group_read(ctx, output_format, group_name):
    """Get details for a single user group"""

    fmtr = _formatter(output_format, _output_handler(), 'group')
    umapi_conn = ctx.obj['conn']
    query = umapi_client.GroupsQuery(umapi_conn)
    matched = [g for g in query if normalize(g['groupName']) == normalize(group_name)]
    if len(matched) > 0:
        fmtr.record(matched[0])
        fmtr.write()
    else:
        click.echo(f"Group '{group_name}' not found")


@app.command()
@click.help_option('-h', '--help')
@click.option('-f', '--format', 'output_format', help='Output format', metavar='csv|json|pretty', default='pretty',
              show_default=True)
@click.option('-o', '--out-file', help='Write output to this filename', metavar='FILENAME')
@click.pass_context
def group_read_all(ctx, output_format, out_file):
    """Get details for all groups in a console"""
    fmtr = _formatter(output_format, _output_handler(out_file), 'group')
    umapi_conn = ctx.obj['conn']
    query = umapi_client.GroupsQuery(umapi_conn)
    for group in query:
        fmtr.record(group)
    fmtr.write()


@app.command()
@click.help_option('-h', '--help')
@click.option('--type', 'user_type', help="User's identity type", metavar='adobeID|enterpriseID|federatedID',
              default='federatedID', show_default=True)
@click.option('--email', help="User's email address", required=True)
@click.option('--username', help="User's username (set to email if omitted)")
@click.option('--domain', help="User's directory domain (set to username domain if omitted, if username is an "
                               "email, this must be set to same domain)")
@click.option('--groups', help="Comma-delimited list of groups to assign user", default='', show_default=False)
@click.option('--firstname', help="User's first name")
@click.option('--lastname', help="User's last name")
@click.option('--country', help="User's two-letter (ISO-3166-1 alpha2) country code", required=True)
@click.pass_context
def user_create(ctx, user_type, email, username, domain, groups, firstname, lastname, country):
    """Create a single user

       Example:

       umapi user-create \
             --type federatedID \
             --email test.user.001@example.com \
             --username test.username.001@example.com \
             --groups group1,group2 \
             --firstname Test \
             --lastname "User 001" \
             --country US
    """
    umapi_conn = ctx.obj['conn']
    queue = ActionQueue(umapi_conn)
    queue.queue_user_create_action(user_type, email, country, firstname, lastname,
                                   username, domain, groups.split(','))
    queue.execute()
    click.echo("errors: {}".format(queue.errors()))


@app.command()
@click.help_option('-h', '--help')
@click.option('-c', '--console-name', help='Short name of the integration config',
              default='main', show_default=True)
@click.option('-f', '--format', 'input_format', help='Input file format', metavar='csv|json', default='csv',
              show_default=True)
@click.option('-i', '--in-file', help='Input filename', metavar='FILENAME')
@click.option('-t', '--test', 'test_mode', help="Run command in test mode", default=False, show_default=False,
              is_flag=True)
def user_create_bulk(console_name, input_format, in_file, test_mode):
    """Create users in bulk from an input file"""
    fmtr = _formatter(input_format, _input_handler(in_file), 'user')
    auth_config = config.read(console_name)
    umapi_conn = client.create_conn(auth_config, test_mode)
    queue = action_queue.ActionQueue(umapi_conn)
    for user in fmtr.read():
        queue.queue_user_action(user_type=user['type'], email=user['email'], username=user['username'],
                                domain=user['domain'], groups=user['groups'], firstname=user['firstname'],
                                lastname=user['lastname'], country=user['country'])
    queue.execute()
    for err in queue.errors():
        click.echo("Error: {}".format(err))


@app.command()
@click.help_option('-h', '--help')
@click.option('-c', '--console-name', help='Short name of the integration config',
              default='main', show_default=True)
@click.option('-e', '--email', help='User email address', required=True)
@click.option('--type', 'user_type', help="User's identity type", metavar='adobeID|enterpriseID|federatedID',
              default='federatedID', show_default=True)
@click.option('-d', '--hard', 'hard_delete',
              help="Delete user from underlying directory instead of just the org level",
              default=False, show_default=False, is_flag=True)
@click.option('-t', '--test', 'test_mode', help="Run command in test mode", default=False, show_default=False,
              is_flag=True)
def user_delete(console_name, email, user_type, hard_delete, test_mode):
    """Delete a single user (from org and/or identity directory)"""
    auth_config = config.read(console_name)
    umapi_conn = client.create_conn(auth_config, test_mode)
    queue = action_queue.ActionQueue(umapi_conn)
    queue.queue_delete_action(user_type, email, hard_delete)
    queue.execute()
    click.echo("errors: {}".format(queue.errors()))


@app.command()
@click.help_option('-h', '--help')
@click.option('-c', '--console-name', help='Short name of the integration config',
              default='main', show_default=True)
@click.option('-f', '--format', 'input_format', help='Input file format', metavar='csv|json', default='csv',
              show_default=True)
@click.option('-i', '--in-file', help='Input filename', metavar='FILENAME')
@click.option('-t', '--test', 'test_mode', help="Run command in test mode", default=False, show_default=False,
              is_flag=True)
def user_delete_bulk(console_name, input_format, in_file, test_mode):
    """Delete users in bulk from input file (from org and/or identity directory)"""
    fmtr = _formatter(input_format, _input_handler(in_file), 'user')
    auth_config = config.read(console_name)
    umapi_conn = client.create_conn(auth_config, test_mode)
    queue = action_queue.ActionQueue(umapi_conn)
    for user in fmtr.read():
        queue.queue_delete_action(user['type'], user['email'],
                                  True if user['hard_delete'].strip().lower() == 'y' else False)
    queue.execute()
    for err in queue.errors():
        click.echo("Error: {}".format(err))


@app.command()
@click.help_option('-h', '--help')
@click.option('-c', '--console-name', help='Short name of the integration config',
              default='main', show_default=True)
@click.option('-e', '--email', help='User email address', required=True)
@click.option('-E', '--email-new', help="User's new email address", required=False)
@click.option('-f', '--firstname', help="User's first name", required=False)
@click.option('-l', '--lastname', help="User's last name", required=False)
@click.option('-u', '--username', help="User's username", required=False)
@click.option('-C', '--country', help="User's country code", required=False)
@click.option('--type', 'user_type', help="User's identity type", metavar='adobeID|enterpriseID|federatedID',
              default='federatedID', show_default=True)
@click.option('-t', '--test', 'test_mode', help="Run command in test mode", default=False, show_default=False,
              is_flag=True)
def user_update(console_name, email, email_new, firstname, lastname, username, country, user_type, test_mode):
    """Update user information for a single user"""
    auth_config = config.read(console_name)
    umapi_conn = client.create_conn(auth_config, test_mode)
    queue = action_queue.ActionQueue(umapi_conn)
    queue.queue_update_action(user_type, email, email_new, firstname, lastname, username, country)
    queue.execute()
    click.echo("errors: {}".format(queue.errors()))


@app.command()
@click.help_option('-h', '--help')
@click.option('-c', '--console-name', help='Short name of the integration config',
              default='main', show_default=True)
@click.option('-f', '--format', 'input_format', help='Input file format', metavar='csv|json', default='csv',
              show_default=True)
@click.option('-i', '--in-file', help='Input filename', metavar='FILENAME')
@click.option('-t', '--test', 'test_mode', help="Run command in test mode", default=False, show_default=False,
              is_flag=True)
def user_update_bulk(console_name, input_format, in_file, test_mode):
    """Update users in bulk from input file"""
    fmtr = _formatter(input_format, _input_handler(in_file), 'user')
    auth_config = config.read(console_name)
    umapi_conn = client.create_conn(auth_config, test_mode)
    queue = action_queue.ActionQueue(umapi_conn)
    for user in fmtr.read():
        queue.queue_update_action(user['type'], user['email'], user['email_new'], user['firstname'],
                                  user['lastname'], user['username'], user['country'])
    queue.execute()
    for err in queue.errors():
        click.echo("Error: {}".format(err))


if __name__ == '__main__':
    app()
