# CLI reference

Generated from the parser by
`scripts/gen_cli_reference.py`. Do not edit by hand.

## `selfproof start`

usage: selfproof start [-h] [--gates GATES]

- `-h, --help`: show this help message and exit
- `--gates`: comma-separated gate names (default: all)

## `selfproof init`

usage: selfproof init [-h] [--force]

- `-h, --help`: show this help message and exit
- `--force`: overwrite existing files

## `selfproof status`

usage: selfproof status [-h]

- `-h, --help`: show this help message and exit

## `selfproof build`

usage: selfproof build [-h] [--gates GATES]

- `-h, --help`: show this help message and exit
- `--gates`: comma-separated gate names (default: all)

## `selfproof ledger`

usage: selfproof ledger [-h] {verify} ...

- `-h, --help`: show this help message and exit
- `ledger_command`: 

## `selfproof rules`

usage: selfproof rules [-h] {generate,check} ...

- `-h, --help`: show this help message and exit
- `rules_command`: 

## `selfproof dashboard`

usage: selfproof dashboard [-h] {show,export,open} ...

- `-h, --help`: show this help message and exit
- `dashboard_command`: 

## `selfproof improve`

usage: selfproof improve [-h] {measure,ratchet} ...

- `-h, --help`: show this help message and exit
- `improve_command`: 

## `selfproof release`

usage: selfproof release [-h] {check,sbom} ...

- `-h, --help`: show this help message and exit
- `release_command`: 

## `selfproof fleet`

usage: selfproof fleet [-h] {scan} ...

- `-h, --help`: show this help message and exit
- `fleet_command`: 

## `selfproof bench`

usage: selfproof bench [-h] {report} ...

- `-h, --help`: show this help message and exit
- `bench_command`: 

## `selfproof autopilot`

usage: selfproof autopilot [-h] [--gates GATES]

- `-h, --help`: show this help message and exit
- `--gates`: comma-separated gate names (default: all)
