# User Management API CLI Tool

A simple command-line interface (CLI) client to the
[Adobe User Management API](https://adobe-apiplatform.github.io/umapi-documentation/en/).

## Table of Contents

* [Feature Overview](#feature-overview)
* [Installation](#installation)
* [Usage Overview](#usage-overview)
* [Configuring](#configuring)
* [Commands](#commands)
* [Appendix: Building the Tool](#appendix-building-the-tool)
* [Getting Help](#getting-help)

# Feature Overview

**User Operations**

* [Query a Single User](#user-read)
* [Query All Users](#user-read-all)
* [Create Single User](#user-create)
* [Create Users in Bulk](#user-create-bulk)
* [Update a User](#user-update)
* [Update Users in Bulk](#user-update-bulk)
* [Remove or Delete a User](#user-delete)
* [Remove or Delete Users in Bulk](#user-delete-bulk)

**Group Operations**

* [Query a Single Group](#group-read)
* [Query All Groups](#group-read-all)
* [Create Single Group](#group-create)
* [Create Groups in Bulk](#group-create-bulk)
* [Update a Group](#group-update)
* [Update Groups in Bulk](#group-update-bulk)
* [Delete a Group](#group-delete)
* [Delete Groups in Bulk](#group-delete-bulk)

"bulk" and "all" operations support multiple input/output formats.

"Read All" output formats:

* Human-readable
* CSV
* [JSONL](http://jsonlines.org)

Bulk create/update/delete formats:

* CSV
* [JSONL](http://jsonlines.org)

# Installation

The recommended method for installing the tool is
[pipx](https://pypa.github.io/pipx/). It not only installs the tool in an
isolated environment, but also makes it available on the shell's `$PATH`
variable.

You can alternatively download the tool as a self-contained executable for
Windows or macOS. Check the [releases
page](https://github.com/adobe/umapi-cli/releases/) for the latest stable
release. Source distributions and wheel builds are also published on each new
release.

## Option 1 - `pipx`

On a system with [pipx](https://pypa.github.io/pipx/installation/) installed,
installing the UMAPI CLI Tool is simple:

``` sh
$ pipx install umapi-cli
```

This puts the `umapi` executable in your shell's `$PATH` and makes it available
from any directory.

``` sh
$ umapi --help
```

## Option 2 - Executable

A self-contained executable is also available for Windows and macOS. The
executable embeds a Python environment, so Python does not need to be installed
on the system. Note that this build is slower to start when executing the tool.

# Usage Overview

The tool operates on a series of commands. Each command performs a certain
operation - read single user, read all users, create user/group, etc.

```
$ umapi --help
Usage: umapi [OPTIONS] COMMAND [ARGS]...

Options:
  --env PATH  Path to .env file (optional)
  -t, --test  Run command in test mode
  -v          Enable verbose logging
  -h, --help  Show this message and exit.
  --version   Show the version and exit.

Commands:
  group-create       Create a single user group.
  group-create-bulk  Create groups in bulk from an input file
  group-delete       Delete a single user group
  group-delete-bulk  Delete groups in bulk from input file
  group-read         Get details for a single user group
  group-read-all     Get details for all groups in a console
  group-update       Update information/memberships for a single group
  group-update-bulk  Update groups in bulk from input file
  user-create        Create a single user.
  user-create-bulk   Create users in bulk from an input file
  user-delete        Delete a single user (from org and/or identity...
  user-delete-bulk   Delete users in bulk from input file (from org...
  user-read          Get details for a single user
  user-read-all      Get details for all users belonging to a console
  user-update        Update user information for a single user
  user-update-bulk   Update users in bulk from input file
```

## General Options

The following options apply to any command. They should be specified before the
command being invoked.

For example, to invoke test mode when creating a list of users from a CSV file:

```
$ umapi -t user-create-bulk -f csv -i users.csv
```

The following general options apply to any UMAPI command:

* `--env` - Specify an `env` file containing UMAPI configuration. If this isn't
  specified, then the tool will look for a `.env` file in the current working
  directory. If that isn't present then it will look for the `UMAPI_*`
  environment variables mentioned above, which define config options for the
  UMAPI connection.
* `-t/--test` - Invoke test mode for all UMAPI calls made when running the
  command. Test mode performs all API actions in a "dry run" mode which will
  return results as if the actions were executed, but not perform any actual
  changes to users or groups in the Admin Console. This can also be used for
  user and group read operations, but it does not affect the output of the read
  operation.
* `-v` - Enable logging and control verbosity. Pass `-v` to enable `info` level
  logging. Pass `-vv` to log with more information at the `debug` level. If
  neither option is passed, then the tool will only pass output for errors and
  the results of read operations. **Note:** the tool logs output to stdout.
  Redirect stdout to a file to capture log information.

# Configuring

The CLI tool requires a valid connection to the User Management API. This must
be set up in the [Adobe Developer Console](https://developer.adobe.com/console)
prior to using the tool.

Refer to [this
guide](https://developer.adobe.com/developer-console/docs/guides/authentication/ServerToServerAuthentication/implementation/)
if you need help creating the API integration and credentials. Once setup is
complete, you need three items from the credential page:

* `client_id` - Unique identifier to authorize the API client
* `client_secret` - Secret token to authenticate the connection
* `org_id` - Unique organization identifier

The UMAPI CLI Tool expects these items to be set in the following evironment variables.

* `UMAPI_CLIENT_ID`
* `UMAPI_CLIENT_SECRET`
* `UMAPI_ORG_ID`

These can either be set as system variables (e.g. `export
UMAPI_CLIENT_ID=abc123`) or saved to a `.env` file in this format:

```
UMAPI_CLIENT_ID=abc-123
UMAPI_CLIENT_SECRET=xyz-9876
UMAPI_ORG_ID=ABC123@AdobeOrg
```

Save this to a file with the name `.env` and the UMAPI CLI Tool will read it if
it is present in the current working directory.

> **NOTE:** You are responsible for keeping this file safe. Limit access to it
> to prevent unauthorized access.

For most users, it is sufficient to provide the Client ID, Client Secret and Org
ID. There are, however, cases where the auth or UMAPI endpoints need to be
customized. They can be set with these variables:

* `UMAPI_AUTH_HOST` - Hostname of auth endpoint server
* `UMAPI_AUTH_ENDPOINT` - Path portion of auth endpoint
* `UMAPI_URL` - Full URI to UMAPI endpoint

If you are working with more than one target, you can specify an alternative env
file with the `--env` option.

```
$ umapi --env .env-secondary user-read-all
```

The above example reads UMAPI config from the file `.env-secondary` since this
file isn't named `.env`, it won't be read automatically. To read it, we pass the
`--env` option before we specify the command (`user-read-all` in this case).

# Commands

## `user-read`

Get details for a single user by email address. 

Change the output format with the option `-f/--format`. Supported formats: JSON,
CSV, or human-readable (default.)

```
$ umapi user-read -e user@example.com
email     : user@example.com
groups    : ['All Apps', 'Adobe Stock']
username  : user@example.com
domain    : example.com
firstname : Example
lastname  : User
country   : US
type      : federatedID
```

Usage:

```
$ umapi user-read --help
Usage: umapi user-read [OPTIONS]

  Get details for a single user

Options:
  -h, --help                    Show this message and exit.
  -f, --format csv|json|pretty  Output format  [default: pretty]
  -e, --email TEXT              User email address  [required]
```

## `user-read-all`

Get details for all users in a given console. 

Formats: [JSONL](http://jsonlines.org), CSV, or human-readable (default).

This command writes to stdout by default, but can optionally write output to a
given filename.

```
# write all users to a CSV file
$ umapi user-read-all -f csv -o users.csv
```

Usage:

```
$ umapi user-read-all --help
Usage: umapi user-read-all [OPTIONS]

  Get details for all users belonging to a console

Options:
  -h, --help                    Show this message and exit.
  -f, --format csv|json|pretty  Output format  [default: pretty]
  -o, --out-file FILENAME       Write output to this filename
```

Names of columns/fields when writing to CSV or JSONL are the same.

| Column Name | Purpose                                                               |
|-------------|-----------------------------------------------------------------------|
| `type`      | User's identity type (`enterpriseID`, `federatedID` or `adobeID`)     |
| `firstname` | User's given (first) name                                             |
| `lastname`  | User's surname (last name)                                            |
| `email`     | User's email address                                                  |
| `username`  | SSO username of user                                                  |
| `domain`    | If the user is in a claimed domain, this is the domain they belong to |
| `country`   | Two-letter country code indicating country of user                    |
| `groups`    | List* of groups to which user is assigned                             |

\* in JSONL, groups are represented as a JSON list. In CSV, groups are
serialised to a comma-delimited list (enclosed in double quotes).

## `user-create`

Create a single user.

Example:

```
$ umapi user-create --type federatedID --email test.user.001@example.com \
  --username test.user.001@example.com --groups "All Apps,Adobe Sign" \
  --firstname Test --lastname "User 001" --country US
```

Usage:

```
$ umapi user-create --help
Usage: umapi user-create [OPTIONS]

  Create a single user.

Options:
  -h, --help                      Show this message and exit.
  --type adobeID|enterpriseID|federatedID
                                  User's identity type  [default: federatedID]
  --email TEXT                    User's email address  [required]
  --username TEXT                 User's username (set to email if omitted)
  --domain TEXT                   User's directory domain (set to username
                                  domain if omitted, if username is an email,
                                  this must be set to same domain)
  --groups TEXT                   Comma-delimited list of groups to assign
                                  user
  --firstname TEXT                User's first name
  --lastname TEXT                 User's last name
  --country TEXT                  User's two-letter (ISO-3166-1 alpha2)
                                  country code  [required]
```

## `user-create-bulk`

Create users in bulk from an input file.

Formats: [JSONL](http://jsonlines.org) or CSV (default)

Expects `-i/--in-file` option that specifies input file path.

Example - create all users specified in "users.csv"

```
$ umapi user-create-bulk -f csv -i users.csv
```

Usage:

```
$ umapi user-create-bulk --help
Usage: umapi user-create-bulk [OPTIONS]

  Create users in bulk from an input file

Options:
  -h, --help              Show this message and exit.
  -f, --format csv|json   Input file format  [default: csv]
  -i, --in-file FILENAME  Input filename
```

The columns/fields expected by `user-create-bulk` are named and formatted in the
same way as output from `user-read-all`.

| Column Name | Purpose                                                               |
|-------------|-----------------------------------------------------------------------|
| `type`      | User's identity type (`enterpriseID`, `federatedID` or `adobeID`)     |
| `firstname` | User's given (first) name                                             |
| `lastname`  | User's surname (last name)                                            |
| `email`     | User's email address                                                  |
| `username`  | SSO username of user                                                  |
| `domain`    | If the user is in a claimed domain, this is the domain they belong to |
| `country`   | Two-letter country code indicating country of user                    |
| `groups`    | List* of groups to which user is assigned                             |

\* in JSONL, groups are represented as a JSON list. In CSV, groups are
serialised to a comma-delimited list (enclosed in double quotes).

## `user-update`

Update a single user.

Example:

```
$ umapi user-update
  --email test.user.001@example.com \
  --firstname Test \
  --lastname "Username 001"
```

Usage:

```
$ umapi user-update --help
Usage: umapi user-update [OPTIONS]

  Update user information for a single user

Options:
  -h, --help                Show this message and exit.
  -e, --email TEXT          Email address that identifies the user  [required]
  -E, --email-new TEXT      Updated email address
  -f, --firstname TEXT      Updated given (first) name
  -l, --lastname TEXT       Updated surname (last name)
  -u, --username TEXT       Updated username
  -g, --groups-add TEXT     Comma-delimited list of groups to add for user
  -G, --groups-remove TEXT  Comma-delimited list of groups to remove from user
```

When updating a user, the email address is required to identify the user. The
`-e/--email` option specifies the identifying email address. `-u/--username` is
used to specify a new username when updating the username field.

Apart from `-e/--email`, all other options are not required.

## `user-update-bulk`

Update users in bulk from an input file.

Formats: [JSONL](http://jsonlines.org) or CSV (default)

Expects `-i/--in-file` option that specifies input file path.

Example - create all users specified in "users.csv"

```
$ umapi user-update-bulk -f csv -i users.csv
```

Usage:

```
$ umapi user-update-bulk --help
Usage: umapi user-update-bulk [OPTIONS]

  Update users in bulk from input file

Options:
  -h, --help              Show this message and exit.
  -f, --format csv|json   Input file format  [default: csv]
  -i, --in-file FILENAME  Input filename
```

This is the expected format of an input file for bulk updating users:

| Column Name     | Purpose                                        |
|-----------------|------------------------------------------------|
| `email`         | User's email address                           |
| `email_new`     | New email address to assign user               |
| `username`      | New username to assign                         |
| `firstname`     | Updated given (first) name                     |
| `lastname`      | Updated surname (last name)                    |
| `add_groups`    | List* of group assignments to add for user     |
| `remove_groups` | List* of group assignments to remove from user |

\* in JSONL, groups are represented as a JSON list. In CSV, groups are
serialised to a comma-delimited list (enclosed in double quotes).

## `user-delete`

Delete a single user from a given Admin Console.

There are two kinds of deletion:

* **soft** - remove the user from the Console user list, but not the underlying identity directory (default)
* **hard** - remove the user from the underlying identity directory (the "Directory Users" list)

**NOTE:** Hard-deleting may only be done on the Console that owns the directory. Trusted 
directories only support soft-deletion.

Example:

```
# soft-delete user test.user.001@example.com
$ umapi user-delete --email test.user.001@example.com

# hard-delete user test.user.002@example.com
$ umapi user-delete --email test.user.001@example.com --hard
```

Usage:

```
$ umapi user-delete --help
Usage: umapi user-delete [OPTIONS]

  Delete a single user (from org and/or identity directory)

Options:
  -h, --help        Show this message and exit.
  -e, --email TEXT  User email address  [required]
  -d, --hard        Delete user from underlying directory instead of just the
                    org level
```

## `user-delete-bulk`

Delete a list of users from an input file.

Formats: [JSONL](http://jsonlines.org) or CSV (default)

See [notes above](#user-delete) about deletion types.

Expects `-i/--in-file` option that specifies input file path.

```
# delete all users specified in "delete_users.csv"
$ umapi user-delete-bulk -i delete_users.csv -f csv
```

Usage:

```
$ umapi user-delete-bulk --help
Usage: umapi user-delete-bulk [OPTIONS]

  Delete users in bulk from input file (from org and/or identity directory)

Options:
  -h, --help              Show this message and exit.
  -f, --format csv|json   Input file format  [default: csv]
  -i, --in-file FILENAME  Input filename
```

The input file should specify two fields - the email address to identify each
user, and whether or not to hard-delete.

| Column Name   | Purpose                                                    |
|---------------|------------------------------------------------------------|
| `email`       | Email address of user                                      |
| `hard_delete` | `Y` or `y` to hard-delete user. `N` or `n` to soft-delete. |

## `group-read`

Get details for a single group based on a given group name.

Example:

```
$ umapi group-read -g 'Adobe Sign'
groupName      : Adobe Sign
type           : PRODUCT_PROFILE
adminGroupName : _admin_Adobe Sign
memberCount    : 3
productName    : Adobe Sign-Enterprise
licenseQuota   : 10
```

The group name is case-insensitive.

Usage:

```
$ umapi group-read --help
Usage: umapi group-read [OPTIONS]

  Get details for a single user group

Options:
  -h, --help                    Show this message and exit.
  -f, --format csv|json|pretty  Output format  [default: pretty]
  -g, --group TEXT              Group name  [required]
```

## `group-read-all`

Get details for all groups in a given console.

Formats: [JSONL](http://jsonlines.org), CSV, or human-readable (default.)

This command writes to stdout by default, but can optionally write output to a given filename.

Example:

```
# write all groups to a CSV file
$ umapi group-read-all -f csv -o groups.csv
```

Usage:

```
$ umapi group-read-all --help
Usage: umapi group-read-all [OPTIONS]

  Get details for all groups in a console

Options:
  -h, --help                    Show this message and exit.
  -f, --format csv|json|pretty  Output format  [default: pretty]
  -o, --out-file FILENAME       Write output to this filename
```

`group-read-all` outputs the same fields regardless of the format in use.

| Column Name      | Purpose                                                                  |
|------------------|--------------------------------------------------------------------------|
| `groupName`      | Name of group                                                            |
| `type`           | Group type - `PRODUCT_PROFILE`, `USER_GROUP`, etc                        |
| `adminGroupName` | Name of the admin group associated with this group                       |
| `memberCount`    | Number of users who belong to this group                                 |
| `productName`    | If this is a product profile, this is the name of the associated product |
| `licenseQuota`   | License quota setting if group is a product profile                      |

## `group-update`

Update a single user group. This command also allows the management of users and
profiles for a given group.

Example:

```
$ umapi group-update
  --name "Test Group" \
  --name-new "Updated Test Group" \
  --users-add "test.user.01@example.com,test.user.02@example.com"
```

Usage:

```
$ umapi group-update --help
Usage: umapi group-update [OPTIONS]

  Update information/memberships for a single group

Options:
  -h, --help                  Show this message and exit.
  -n, --name TEXT             Current name of group  [required]
  -N, --name-new TEXT         New name to assign group
  -d, --description TEXT      Updated group description
  -u, --users-add TEXT        Comma-delimited list of email addresses of users
                              to assign
  -U, --users-remove TEXT     Comma-delimited list of email addresses of users
                              to remove
  -p, --profiles-add TEXT     Comma-delimited list of product profiles to
                              associate with group
  -P, --profiles-remove TEXT  Comma-delimited list of product profiles to
                              remove from group
```

The group name, `-n/--name` is required to identify the group. All other options
are optional.

## `group-update-bulk`

Update groups in bulk from an input file.

Formats: [JSONL](http://jsonlines.org) or CSV (default)

Expects `-i/--in-file` option that specifies input file path.

Example - create all users specified in "groups.csv"

```
$ umapi group-update-bulk -f csv -i groups.csv
```

Usage:

```
$ umapi group-update-bulk --help
Usage: umapi group-update-bulk [OPTIONS]

  Update groups in bulk from input file

Options:
  -h, --help              Show this message and exit.
  -f, --format csv|json   Input file format  [default: csv]
  -i, --in-file FILENAME  Input filename
```

This is the expected format of an input file for bulk updating groups:

| Column Name       | Purpose                                               |
|-------------------|-------------------------------------------------------|
| `name`            | Current name of group                                 |
| `name_new`        | Updated group name                                    |
| `description`     | Updated group description                             |
| `add_users`       | List* of users to assign to group                     |
| `remove_users`    | List* of users to remove from membeship of this group |
| `add_profiles`    | List* of product profiles to assign to user group     |
| `remove_profiles` | List* of product profiles to remove from group        |

\* in JSONL, users/profiles are represented as a JSON list. In CSV, they are
serialised to a comma-delimited list (enclosed in double quotes).

## `group-delete`

Delete a single user group.

Example:

```
$ umapi group-delete --name "Test Group"
```

Usage:

```
$ umapi group-delete --help
Usage: umapi group-delete [OPTIONS]

  Delete a single user group

Options:
  -h, --help       Show this message and exit.
  -n, --name TEXT  Group name  [required]
```

## `group-delete-bulk`

Delete a list of groups from an input file.

Formats: [JSONL](http://jsonlines.org) or CSV (default)

Expects `-i/--in-file` option that specifies input file path.

Example:

```
$ umapi group-delete-bulk -i delete_groups.csv -f csv
```

Usage:

```
$ umapi group-delete-bulk --help
Usage: umapi group-delete-bulk [OPTIONS]

  Delete groups in bulk from input file

Options:
  -h, --help              Show this message and exit.
  -f, --format csv|json   Input file format  [default: csv]
  -i, --in-file FILENAME  Input filename
```

The input file just requies the name of each group to delete.

| Column Name | Purpose                 |
|-------------|-------------------------|
| `name`      | Name of group to delete |

# Appendix: Building the Tool

1. Clone this repo - `git clone https://github.com/adobe/umapi-cli.git`
2. `cd umapi-cli`
3. Ensure that [Poetry](https://poetry.eustace.io/) is installed.
4. In the project directory, run `make` to build the executable and the package
   distributions. These can be found in the `dist` directory.
   
To run the tool from source:

1. Ensure dependencies are up to date with `poetry install`.
2. Prefix invocations of the `umapi` command with `poetry run` (e.g. `poetry run
   umapi --help`). This runs the `umapi` entrypoint from the project's virtual
   environment.
   
> **Note:** if you are doing development work on the tool and wish to see full
> error information when an error occurs, set the `UMAPI_DEBUG` environment
> variable to `1`. This will dump more information on the error including a
> stack trace.

# Getting Help

Should you run into any issues using this tool, or have any questions or
comments, please create an [issue](https://github.com/adobe/umapi-cli/issues) to
contact the development team.
