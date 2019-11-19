# User Management API CLI Tool

A simple command-line interface (CLI) client to the [Adobe User Management API](https://adobe-apiplatform.github.io/umapi-documentation/en/).

## Feature Overview

* Users
    * Read
    * Update
    * Create
    * Delete
* User Groups
    * Read
    * Update
    * Create
    * Delete

Each command can operate on a single user or on a group of users (e.g. read all users or
create users in bulk from an input file).

"Read All" output formats:

* Human-readable
* CSV
* [JSON](http://jsonlines.org)

Bulk create/update/delete formats:

* CSV
* [JSON](http://jsonlines.org)

## Running in Development (Recommended)

1. Clone this repo - `git clone git@git.corp.adobe.com:dmeservices/umapi-cli.git`
2. `cd umapi-cli`
3. Create a virtual environment - `python -m venv venv` (Python 3.7 or greater required)
4. Activate it `.\venv\Scripts\Activate.ps1` or `source venv/bin/activate`
5. Install [Poetry](https://poetry.eustace.io/)
6. Install dependencies `poetry install`
7. An executable will be created in `venv\Scripts` or `venv/bin` called `umapi` - use this command to run the tool

## Running the Executable

Standalone executables can be found on the Releases page. These builds do not require Python to run.
Since they embed Python, they are inherently a bit slower to run than the package build.

## Usage Overview

The tool operates on a series of commands.

```
$ umapi --help
Usage: umapi [OPTIONS] COMMAND [ARGS]...

Options:
  -h, --help  Show this message and exit.

Commands:
  group-read        Get details for a single user group
  group-read-all    Get details for all groups in a console
  init              Initialize a new UMAPI client config
  user-create       Create a single user
  user-create-bulk  Create users in bulk from an input file
  user-delete       Delete a single user (from org and/or identity...
  user-delete-bulk  Delete users in bulk from input file (from org and/or...
  user-read         Get details for a single user
  user-read-all     Get details for all users belonging to a console
```

Before running any user or group command, it is necessary to initialize the tool with a 
UMAPI configuration. The command `init` will create a new UMAPI config in the **current 
working directory** (under `.config/`).

**NOTE:** We recommend establishing a working directory to use this tool (e.g. `~/umapi-cli`).
This ensures that the `.config` directory does not conflict with any system-related config
directories.

UMAPI operation commands use the form `noun-verb[-modifier]` (e.g. `user-read` or `group-update-bulk`).

All UMAPI operation commands implement `-c/--console-name` to target alternate Admin Console
connections.

### `init`

Initialize a new UMAPI client configuration. Will prompt for required UMAPI integration details.

See the [Adobe.IO documentation](https://www.adobe.io/authentication/auth-methods.html#!AdobeDocs/adobeio-auth/master/AuthenticationOverview/ServiceAccountIntegration.md)
for creating a UMAPI integration and getting credentials.

Once you have an integration for the User Management API, the credentials required by `init`
can be found on the Integration Details page for the integration. The path to the private key file
is also required.

Running `umapi init` with no additional parameters with interactively prompt you for each
piece of UMAPI configuration it needs and store this in a config file called "main".

Additional UMAPI connections can be configured by setting the `-c` or `--console-name` option.
The console name should be a short alphanumeric identifier (e.g. `-c stock_console`).

```
$ umapi init
Organization ID: [org id]
Tech Account ID: [tech account ID (not email)]
API Key: [api key]
Client Secret: [client secret]
Private Key Path [private.key]: /path/to/private.key
Delete private key file? [y/N]: y
```

These configuration items can also be set as options to avoid the interactive prompt.

```
$ umapi init --help
Usage: umapi init [OPTIONS]

  Initialize a new UMAPI client config

Options:
  -h, --help               Show this message and exit.
  --org-id TEXT            Organization ID
  --tech-acct TEXT         Tech Account ID
  --api-key TEXT           API Key
  --client-secret TEXT     Client Secret
  --priv-key TEXT          Private Key Path
  -d / -D                  Delete private key file (or do not delete it)
  -c, --console-name TEXT  Short name to assign to the integration config
                           [default: main]
  -o                       Overwrite existing config
```

### `user-read`

Get details for a single user by email address. 

Formats: JSON, CSV, or human-readable (default.)

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
  -c, --console-name TEXT       Short name of the integration config
                                [default: main]
  -f, --format csv|json|pretty  Output format  [default: pretty]
  -e, --email TEXT              User email address  [required]
```

### `user-read-all`

Get details for all users in a given console. 

Formats: [JSON](http://jsonlines.org), CSV, or human-readable (default.)

This command writes to stdout by default, but can optionally write output to a given filename.

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
  -c, --console-name TEXT       Short name of the integration config
                                [default: main]
  -f, --format csv|json|pretty  Output format  [default: pretty]
  -o, --out-file FILENAME       Write output to this filename
```

### `user-create`

Create a single user.

```
$ umapi user-create --type federatedID --email test.user.001@example.com \
  --username test.user.001@example.com --groups "All Apps,Adobe Sign" \
  --firstname Test --lastname "User 001" --country US
```

Usage:

```
$ umapi user-create --help
Usage: umapi user-create [OPTIONS]

  Create a single user

Options:
  -h, --help                      Show this message and exit.
  -c, --console-name TEXT         Short name of the integration config
                                  [default: main]
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
  -t, --test                      Run command in test mode
```

### `user-create-bulk`

Create users in bulk from an input file.

Formats: [JSON](http://jsonlines.org) or CSV (default)

Expects `-i/--in-file` option that specifies input file path.

```
# create all users specified in "users.csv"
$ umapi user-create-bulk -f csv -i users.csv
```

Usage:

```
$ umapi user-create-bulk --help
Usage: umapi user-create-bulk [OPTIONS]

  Create users in bulk from an input file

Options:
  -h, --help               Show this message and exit.
  -c, --console-name TEXT  Short name of the integration config  [default:
                           main]
  -f, --format csv|json    Input file format  [default: csv]
  -i, --in-file FILENAME   Input filename
  -t, --test               Run command in test mode
```

### `user-delete`

Delete a single user from a given Admin Console.

There are two kinds of deletion:

* **soft** - remove the user from the Console user list, but not the underlying identity directory (default)
* **hard** - remove the user from the underlying identity directory (the "Directory Users" list)

**NOTE:** Hard-deleting may only be done on the Console that owns the directory. Trusted 
directories only support soft-deletion. Hard-deleting a user will delete **all** cloud
assets associated with the user.

```
# soft-delete user test.user.001@example.com
$ umapi user-delete --email test.user.001@example.com
```

Usage:

```
$ umapi user-delete --help
Usage: umapi user-delete [OPTIONS]

  Delete a single user (from org and/or identity directory)

Options:
  -h, --help                      Show this message and exit.
  -c, --console-name TEXT         Short name of the integration config
                                  [default: main]
  -e, --email TEXT                User email address  [required]
  --type adobeID|enterpriseID|federatedID
                                  User's identity type  [default: federatedID]
  -d, --hard                      Delete user from underlying directory
                                  instead of just the org level
  -t, --test                      Run command in test mode
```

### `user-delete-bulk`

Delete a list of users from an input file.

Formats: [JSON](http://jsonlines.org) or CSV (default)

See [notes above](#user-delete) about deletion types.

Expects `-i/--in-file` option that specifies input file path.

See [format spec](#user-delete-bulk-1) below for column/field spec.

```
# delete all users specified in "delete_users.csv"
$ user-delete-bulk -i delete_users.csv
```

Usage:

```
$ umapi user-delete-bulk --help
Usage: umapi user-delete-bulk [OPTIONS]

  Delete users in bulk from input file (from org and/or identity directory)

Options:
  -h, --help               Show this message and exit.
  -c, --console-name TEXT  Short name of the integration config  [default:
                           main]
  -f, --format csv|json    Input file format  [default: csv]
  -i, --in-file FILENAME   Input filename
  -t, --test               Run command in test mode
```

### `group-read`

Get details for a single group based on a given group name.

```
$ umapi group-read -g 'Adobe Sign'
groupName      : Adobe Sign
type           : PRODUCT_PROFILE
adminGroupName : _admin_Adobe Sign
memberCount    : 3
productName    : Adobe Sign-Enterprise
licenseQuota   : 10
```

Usage:

```
$ umapi group-read --help
Usage: umapi group-read [OPTIONS]

  Get details for a single user group

Options:
  -h, --help                    Show this message and exit.
  -c, --console-name TEXT       Short name of the integration config
                                [default: main]
  -f, --format csv|json|pretty  Output format  [default: pretty]
  -g, --group TEXT              Group name  [required]
```

### `group-read-all`

Get details for all groups in a given console.

Formats: [JSON](http://jsonlines.org), CSV, or human-readable (default.)

This command writes to stdout by default, but can optionally write output to a given filename.

```
# write all groups to a CSV file
$ umapi user-group-all -f csv -o groups.csv
```

Usage:

```
$ umapi group-read-all --help
Usage: umapi group-read-all [OPTIONS]

  Get details for all groups in a console

Options:
  -h, --help                    Show this message and exit.
  -c, --console-name TEXT       Short name of the integration config
                                [default: main]
  -f, --format csv|json|pretty  Output format  [default: pretty]
  -o, --out-file FILENAME       Write output to this filename
```

## Formats

The input and output formats of each UMAPI operation command.

### `user-read` and `user-read-all`

`user-read` and `user-read-all` output the same columns for each user regardless of output
format.

| field | notes |
|---|---|
| `firstname` | User's first name |
| `lastname` | User's surname |
| `email` | User's email address |
| `username` | User's username |
| `domain` | User's domain (governs which Admin Console directory membership) |
| `type` | Account type `federateID`, `enterpriseID` or `adobeID` |
| `country` | User's ISO-3166-1 alpha-2 country code |
| `groups` | List of groups assigned (or to be assigned) to the user |

### `user-create-bulk`

`user-create-bulk` expects the same fields as those documented in the output format for
`user-read` and `user-read-all`. Both CSV and JSON follow the same field name spec with
the following exceptions.

* In CSV input files, the `groups` field should be a comma-delimited list of group names
* In JSON, `groups` is an array of group names

### `user-delete-bulk`

Expected fields are the same for the CSV and JSON formats.

| field | notes |
|---|---|
| `type` | Identity type (required for validation purposes) |
| `email` | Email address of user |
| `hard_delete` | `Y` or `y` to hard-delete user. Any other value will soft-delete. |
