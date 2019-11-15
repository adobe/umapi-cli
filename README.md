# User Management API CLI Tool

A simple command-line interface (CLI) client to the Adobe User Management API.

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
* [jsonl](http://jsonlines.org)

Bulk create/update/delete formats:

* CSV
* [jsonl](http://jsonlines.org)

## Running in Development (Recommended)

1. Clone this repo - `git clone git@git.corp.adobe.com:dmeservices/umapi-cli.git`
2. `cd umapi-cli`
3. Create a virtual environment - `python -m venv venv` (Python 3.7 or greater required)
4. Activate it `.\venv\Scripts\Activate.ps1` or `source venv/bin/sctivate`
5. Install [Poetry](https://poetry.eustace.io/)
6. Install dependencies `poetry install`
7. An executable will be created in `venv\Scripts` or `venv/bin` called `umapi` - use this command to run the tool

## Running the Executable

Standalone executables can be found on the Releases page. These builds do not require Python to run.
Since they embed Python, they are inherently a bit slower to run than the package build.

## Usage Overview

The tool operates on a series of commands.

```shell script
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

```shell script
$  umapi init
Organization ID: [org id]
Tech Account ID: [tech account ID (not email)]
API Key: [api key]
Client Secret: [client secret]
Private Key Path [private.key]: /path/to/private.key
Delete private key file? [y/N]: y
```

These configuration items can also be set as options to avoid the interactive prompt.

```shell script
$  umapi init --help
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
