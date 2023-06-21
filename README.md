# User Management API CLI Tool

A simple command-line interface (CLI) client to the
[Adobe User Management API](https://adobe-apiplatform.github.io/umapi-documentation/en/).

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

Each command can operate on a single user or on a group of users (e.g. read all
users or create users in bulk from an input file).

"Read All" output formats:

* Human-readable
* CSV
* [JSONL](http://jsonlines.org)

Bulk create/update/delete formats:

* CSV
* [JSONL](http://jsonlines.org)

## Running in Development (Recommended)

1. Clone this repo - `git clone https://github.com/adobe/umapi-cli.git
2. `cd umapi-cli`
3. Install [Poetry](https://poetry.eustace.io/)
4. Install dependencies `poetry install` (this command creates a unique virtual
   environment)
5. Run the tool with `poetry run umapi`

## Running the Executable

Standalone executables can be found on the Releases page. These builds do not
require Python to run. Since they embed Python, they are inherently a bit slower
to run than the package build.

## Usage Overview

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
  group-read        Get details for a single user group
  group-read-all    Get details for all groups in a console
  user-create       Create a single user
  user-create-bulk  Create users in bulk from an input file
  user-delete       Delete a single user (from org and/or identity...
  user-delete-bulk  Delete users in bulk from input file (from org and/or...
  user-read         Get details for a single user
  user-read-all     Get details for all users belonging to a console
  user-update       Update user information for a single user
  user-update-bulk  Update users in bulk from input file
```

### General Options

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

## Configuring

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

> ***NOTE:** You are responsible for keeping this file safe. Limit access to it
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

## Commands

### `user-read`

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

### `user-read-all`

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

### `user-create`

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

### `user-create-bulk`

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

### `user-update`

Update a single user.

```
$ umapi user-update --email test.user.001@example.com --firstname Test \
  --lastname "Username 001"
```

Usage:

```
$ umapi user-update --help
Usage: umapi user-update [OPTIONS]

  Update user information for a single user

Options:
  -h, --help                      Show this message and exit.
  -c, --console-name TEXT         Short name of the integration config
                                  [default: main]

  -e, --email TEXT                User email address  [required]
  -E, --email-new TEXT            User's new email address
  -f, --firstname TEXT            User's first name
  -l, --lastname TEXT             User's last name
  -u, --username TEXT             User's username
  -C, --country TEXT              User's country code
  --type adobeID|enterpriseID|federatedID
                                  User's identity type  [default: federatedID]
  -t, --test                      Run command in test mode
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
