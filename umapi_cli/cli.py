# Copyright 2023 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

import click
import sys
import io
import os
from umapi_client import UserQuery, UsersQuery, GroupsQuery
import dotenv
from pathlib import Path
from umapi_cli import config
from umapi_cli import client
from umapi_cli import formatter
from umapi_cli.action_queue import ActionQueue
from umapi_cli.formatter import normalize, InputHandler, OutputHandler, PassthroughHandler
from umapi_cli import log
from umapi_cli.version import __version__ as app_version

def _formatter(data_format, fh, handler):
    fmtr_class = getattr(formatter, data_format, None)
    if fmtr_class is None:
        click.echo("Unknown format '{}'".format(data_format))
        sys.exit(1)
    return fmtr_class(fh, handler)


def _output_fh(out_file=None):
    if out_file is not None:
        return open(out_file, 'w', encoding='utf-8')
    return sys.stdout


def _input_fh(in_file):
    return open(in_file, 'r')


@click.group()
@click.option('--env', 'env_file', help="Path to .env file (optional)", default=None, type=click.Path())
@click.option('-t', '--test', 'test_mode', help="Run command in test mode", default=False, show_default=False,
              is_flag=True)
@click.option('-v', count=True, help="Enable verbose logging")
@click.help_option('-h', '--help')
@click.version_option(app_version, '--version', message='%(prog)s %(version)s')
@click.pass_context
def app(ctx, env_file, test_mode, v):
    log.init(v)
    if env_file is not None:
        dotenv.load_dotenv(env_file)
    else:
        env_file = dotenv.find_dotenv(usecwd=True)
        if env_file:
            dotenv.load_dotenv(env_file)
    ctx.ensure_object(dict)
    conf = config.get_options()
    ctx.obj['conn'] = client.create_conn(conf, test_mode)


def entry():
    debug = True if os.environ.get('UMAPI_DEBUG') == '1' else False
    try:
        app()
    except Exception as e:
        if not debug:
            click.echo(f"ERROR: {e}")
        else:
            raise e


@app.command()
@click.help_option('-h', '--help')
@click.option('-f', '--format', 'output_format', help='Output format', metavar='csv|json|pretty', default='pretty',
              show_default=True)
@click.option('-e', '--email', help='User email address', required=True)
@click.pass_context
def user_read(ctx, output_format, email):
    """Get details for a single user"""

    fmtr = _formatter(output_format, _output_fh(), OutputHandler('user_read'))
    umapi_conn = ctx.obj['conn']
    user = UserQuery(umapi_conn, email).result()
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

    fmtr = _formatter(output_format, _output_fh(out_file), OutputHandler('user_read'))
    umapi_conn = ctx.obj['conn']
    query = UsersQuery(umapi_conn)
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

    fmtr = _formatter(output_format, _output_fh(), OutputHandler('group_read'))
    umapi_conn = ctx.obj['conn']
    query = GroupsQuery(umapi_conn)
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

    fmtr = _formatter(output_format, _output_fh(out_file), OutputHandler('group_read'))
    umapi_conn = ctx.obj['conn']
    query = GroupsQuery(umapi_conn)
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
@click.option('--groups', help="Comma-delimited list of groups to assign user", required=False)
@click.option('--firstname', help="User's first name")
@click.option('--lastname', help="User's last name")
@click.option('--country', help="User's two-letter (ISO-3166-1 alpha2) country code", required=True)
@click.pass_context
def user_create(ctx, user_type, email, username, domain, groups, firstname, lastname, country):
    """Create a single user."""
    """
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
    if groups is None:
        groups = []
    else:
        groups = groups.split(',')
    queue.queue_user_create_action(user_type, email, country, firstname, lastname,
                                   username, domain, groups)
    queue.execute()
    errors = queue.errors()
    if errors:
        click.echo("One or more errors occurred")
        click.echo(render_errors(errors).strip())
    else:
        click.echo("Create operation succeeded")


@app.command()
@click.help_option('-h', '--help')
@click.option('-f', '--format', 'input_format', help='Input file format', metavar='csv|json', default='csv',
              show_default=True)
@click.option('-i', '--in-file', help='Input filename', metavar='FILENAME')
@click.pass_context
def user_create_bulk(ctx, input_format, in_file):
    """Create users in bulk from an input file"""

    fmtr = _formatter(input_format, _input_fh(in_file), InputHandler('user_create_bulk'))
    umapi_conn = ctx.obj['conn']
    queue = ActionQueue(umapi_conn)
    for user in fmtr.read():
        if user['domain'] == '':
            user['domain'] = None
        queue.queue_user_create_action(id_type=user['type'],
                                       email=user['email'], username=user['username'],
                                       domain=user['domain'], groups=user['groups'],
                                       firstname=user['firstname'],
                                       lastname=user['lastname'],
                                       country=user['country'])
    completed = queue.execute()
    errors = queue.errors()
    print_bulk_summaries(completed, errors)


@app.command()
@click.help_option('-h', '--help')
@click.option('-e', '--email', help='User email address', required=True)
@click.option('-d', '--hard', 'hard_delete',
              help="Delete user from underlying directory instead of just the org level",
              default=False, show_default=False, is_flag=True)
@click.pass_context
def user_delete(ctx, email, hard_delete):
    """Delete a single user (from org and/or identity directory)"""

    umapi_conn = ctx.obj['conn']
    queue = ActionQueue(umapi_conn)
    queue.queue_delete_action(email, hard_delete)
    queue.execute()
    errors = queue.errors()
    if errors:
        click.echo("One or more errors occurred")
        click.echo(render_errors(errors).strip())
    else:
        click.echo("Delete operation succeeded")


@app.command()
@click.help_option('-h', '--help')
@click.option('-f', '--format', 'input_format', help='Input file format', metavar='csv|json', default='csv',
              show_default=True)
@click.option('-i', '--in-file', help='Input filename', metavar='FILENAME')
@click.pass_context
def user_delete_bulk(ctx, input_format, in_file):
    """Delete users in bulk from input file (from org and/or identity directory)"""

    fmtr = _formatter(input_format, _input_fh(in_file), InputHandler('user_delete_bulk'))
    umapi_conn = ctx.obj['conn']
    queue = ActionQueue(umapi_conn)
    for user in fmtr.read():
        queue.queue_delete_action(user['email'],
                                  True if user['hard_delete'] == 'y' else False)
    completed = queue.execute()
    errors = queue.errors()
    print_bulk_summaries(completed, errors)


@app.command()
@click.help_option('-h', '--help')
@click.option('-e', '--email', help='Email address that identifies the user', required=True)
@click.option('-E', '--email-new', help="Updated email address", required=False)
@click.option('-f', '--firstname', help="Updated given (first) name", required=False)
@click.option('-l', '--lastname', help="Updated surname (last name)", required=False)
@click.option('-u', '--username', help="Updated username", required=False)
@click.option('-g', '--groups-add', help="Comma-delimited list of groups to add for user", required=False)
@click.option('-G', '--groups-remove', help="Comma-delimited list of groups to remove from user", required=False)
@click.pass_context
def user_update(ctx, email, email_new, firstname, lastname, username, groups_add, groups_remove):
    """Update user information for a single user"""

    umapi_conn = ctx.obj['conn']
    queue = ActionQueue(umapi_conn)
    if groups_add is not None:
        groups_add = groups_add.split(',')
    if groups_remove is not None:
        groups_remove = groups_remove.split(',')
    queue.queue_update_action(email, email_new=email_new, firstname=firstname,
                              lastname=lastname, username=username, add_groups=groups_add,
                              remove_groups=groups_remove)
    queue.execute()
    errors = queue.errors()
    if errors:
        click.echo("One or more errors occurred")
        click.echo(render_errors(errors).strip())
    else:
        click.echo("Update operation succeeded")


@app.command()
@click.help_option('-h', '--help')
@click.option('-f', '--format', 'input_format', help='Input file format', metavar='csv|json', default='csv',
              show_default=True)
@click.option('-i', '--in-file', help='Input filename', metavar='FILENAME')
@click.pass_context
def user_update_bulk(ctx, input_format, in_file):
    """Update users in bulk from input file"""

    fmtr = _formatter(input_format, _input_fh(in_file), InputHandler('user_update_bulk'))
    umapi_conn = ctx.obj['conn']
    queue = ActionQueue(umapi_conn)
    for user in fmtr.read():
        queue.queue_update_action(**user)
    completed = queue.execute()
    errors = queue.errors()
    print_bulk_summaries(completed, errors)


@app.command()
@click.help_option('-h', '--help')
@click.option('--name', help="Name of group", required=True)
@click.option('--description', help="Optional group description")
@click.pass_context
def group_create(ctx, name, description):
    """Create a single user group."""
    """
       Example:

       umapi group-create \
             --name "Adobe Stock Users" \
             --description "Stock provisioning group"
    """

    umapi_conn = ctx.obj['conn']
    queue = ActionQueue(umapi_conn)
    queue.queue_group_create_action(name, description)
    queue.execute()
    errors = queue.errors()
    if errors:
        click.echo("One or more errors occurred")
        click.echo(render_errors(errors).strip())
    else:
        click.echo("Create operation succeeded")


@app.command()
@click.help_option('-h', '--help')
@click.option('-f', '--format', 'input_format', help='Input file format', metavar='csv|json', default='csv',
              show_default=True)
@click.option('-i', '--in-file', help='Input filename', metavar='FILENAME')
@click.pass_context
def group_create_bulk(ctx, input_format, in_file):
    """Create groups in bulk from an input file"""

    fmtr = _formatter(input_format, _input_fh(in_file), InputHandler('group_create_bulk'))
    umapi_conn = ctx.obj['conn']
    queue = ActionQueue(umapi_conn)
    for group in fmtr.read():
        queue.queue_group_create_action(group['name'], group['description'])
    completed = queue.execute()
    errors = queue.errors()
    print_bulk_summaries(completed, errors)


@app.command()
@click.help_option('-h', '--help')
@click.option('-n', '--name', help='Current name of group', required=True)
@click.option('-N', '--name-new', help="New name to assign group", required=False)
@click.option('-d', '--description', help="Updated group description", required=False)
@click.option('-u', '--users-add', help="Comma-delimited list of email addresses of users to assign", required=False)
@click.option('-U', '--users-remove', help="Comma-delimited list of email addresses of users to remove", required=False)
@click.option('-p', '--profiles-add', help="Comma-delimited list of product profiles to associate with group", required=False)
@click.option('-P', '--profiles-remove', help="Comma-delimited list of product profiles to remove from group", required=False)
@click.pass_context
def group_update(ctx, name, name_new, description, users_add, users_remove, profiles_add, profiles_remove):
    """Update information/memberships for a single group"""

    umapi_conn = ctx.obj['conn']
    queue = ActionQueue(umapi_conn)
    if users_add is not None:
        users_add = users_add.split(',')
    if users_remove is not None:
        users_remove = users_remove.split(',')
    if profiles_add is not None:
        profiles_add = profiles_add.split(',')
    if profiles_remove is not None:
        profiles_remove = profiles_remove.split(',')
    queue.queue_group_update_action(name, name_new=name_new,
                                    description=description, add_users=users_add, remove_users=users_remove,
                                    add_profiles=profiles_add, remove_profiles=profiles_remove)
    queue.execute()
    errors = queue.errors()
    if errors:
        click.echo("One or more errors occurred")
        click.echo(render_errors(errors).strip())
    else:
        click.echo("Update operation succeeded")


@app.command()
@click.help_option('-h', '--help')
@click.option('-f', '--format', 'input_format', help='Input file format', metavar='csv|json', default='csv',
              show_default=True)
@click.option('-i', '--in-file', help='Input filename', metavar='FILENAME')
@click.pass_context
def group_update_bulk(ctx, input_format, in_file):
    """Update groups in bulk from input file"""

    fmtr = _formatter(input_format, _input_fh(in_file), InputHandler('group_update_bulk'))
    umapi_conn = ctx.obj['conn']
    queue = ActionQueue(umapi_conn)
    for group in fmtr.read():
        queue.queue_group_update_action(**group)
    completed = queue.execute()
    errors = queue.errors()
    print_bulk_summaries(completed, errors)


@app.command()
@click.help_option('-h', '--help')
@click.option('-n', '--name', help='Group name', required=True)
@click.pass_context
def group_delete(ctx, name):
    """Delete a single user group"""

    umapi_conn = ctx.obj['conn']
    queue = ActionQueue(umapi_conn)
    queue.queue_group_delete_action(name)
    queue.execute()
    errors = queue.errors()
    if errors:
        click.echo("One or more errors occurred")
        click.echo(render_errors(errors).strip())
    else:
        click.echo("Delete operation succeeded")


@app.command()
@click.help_option('-h', '--help')
@click.option('-f', '--format', 'input_format', help='Input file format', metavar='csv|json', default='csv',
              show_default=True)
@click.option('-i', '--in-file', help='Input filename', metavar='FILENAME')
@click.pass_context
def group_delete_bulk(ctx, input_format, in_file):
    """Delete groups in bulk from input file"""

    fmtr = _formatter(input_format, _input_fh(in_file), InputHandler('group_delete_bulk'))
    umapi_conn = ctx.obj['conn']
    queue = ActionQueue(umapi_conn)
    for group in fmtr.read():
        queue.queue_group_delete_action(group['name'])
    completed = queue.execute()
    errors = queue.errors()
    print_bulk_summaries(completed, errors)


def render_errors(errors):
    i = 1
    error_str = []
    for messages in errors:
        error_str.append(f"Error {i} messages:")
        error_io = io.StringIO()
        fmtr = _formatter('pretty', error_io, PassthroughHandler())
        for message in messages:
            fmtr.record(message)
        fmtr.write()
        error_io.seek(0)
        for l in error_io.getvalue().split('\n'):
            error_str.append('   '+l)
        i += 1
    return '\n'.join(error_str)


def render_summary(summary):
    summary_io = io.StringIO()
    fmtr = _formatter('pretty', summary_io, PassthroughHandler())
    fmtr.record(summary)
    fmtr.write()
    summary_io.seek(0)
    return summary_io.getvalue()

def print_bulk_summaries(completed, errors):
    summary = {
        "Executed": completed,
        "Succeeded": completed-len(errors),
        "Errors": len(errors),
    }
    click.echo("--- Action Summary ---")
    click.echo(render_summary(summary).strip())
    click.echo("----------------------")
    if errors:
        click.echo("--- Error Summary ---")
        click.echo(render_errors(errors).strip())
        click.echo("--------------")


if __name__ == '__main__':
    entry()
