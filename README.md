# `click-complete` - Shell Completion for Click CLI Applications

`click-complete` is a Python library that simplifies the process of adding shell completion support to Click-based CLI applications.

______________________________________________________________________

## Features

- **Shell Completion Generation**: Automatically generate shell completion scripts for your Click CLI applications.
- **Customizable Options**: Add a `--completion` option to your CLI commands to generate completion scripts on the fly.
- **Support for Multiple Shells**: Currently supports `fish` shell, with extensibility for `bash` and `zsh`.
- **File Validation**: Includes a custom `FileType` parameter type for validating file paths and extensions.

______________________________________________________________________

## Installation

You can install `click-complete` via pip:

```bash
pip install click-complete
```

______________________________________________________________________

## Quick Start

### Adding Shell Completion to a Click Command

Use the `completion_option` decorator to add a `--completion` option to your Click command:

```python
import click
from click_complete import completion_option

@click.command()
@completion_option()
def mycli():
    """A sample CLI tool."""
    click.echo("Welcome to my CLI!")

if __name__ == "__main__":
    mycli()
```

Run the command with the `--completion` option to generate a completion script:

```bash
$ mycli --completion fish
# Fish completion script for mycli
```

### Adding a Completion Command to a Click Group

Use the `completion_command` function to add a dedicated `completion` command to your Click group:

```python
import click
from click_complete import completion_command

@click.group()
def cli():
    """A sample CLI group."""
    pass

# Add the completion command
cli.add_command(completion_command(program_name="my_app"))

if __name__ == "__main__":
    cli()
```

Run the `completion` command to generate a completion script:

```bash
$ my_app completion fish
# Fish completion script for my_app
```

### Validating File Paths

Use the `FileType` parameter type to validate file paths and extensions:

```python
import click
from click_complete import FileType

@click.command()
@click.argument("file", type=FileType([".json", ".txt"]))
def validate_file(file):
    """Validate a file path and extension."""
    click.echo(f"File '{file}' is valid!")

if __name__ == "__main__":
    validate_file()
```

Run the command with a valid file path:

```bash
$ validate_file example.json
File 'example.json' is valid!
```

______________________________________________________________________

## API Reference

### `get_completion`

```python
def get_completion(
    cli: Union[click.Group, click.Command],
    program_name: str,
    shell: str
) -> str:
    """
    Generate a shell completion script for the given CLI program.

    Args:
        cli: The Click command or group to generate completion for.
        program_name: The name of the CLI program.
        shell: The type of shell to generate completion for (e.g., 'fish').

    Returns:
        The completion script as a string.

    Raises:
        click.UsageError: If the specified shell is not supported or not found.
    """
```

### `completion_option`

```python
def completion_option(
    *param_decls: str,
    program_name: Optional[str] = None,
    **kwargs: Any,
) -> _Decorator[FC]:
    """
    A decorator to add an option for generating shell completion scripts.

    Parameters:
        param_decls: Names of the option (e.g., "--completion").
        program_name: The name of the program. If not provided, it will be inferred.
        kwargs: Additional keyword arguments passed to `click.option`.

    Returns:
        A Click decorator for adding the completion option.
    """
```

### `completion_command`

```python
def completion_command(
    program_name: Optional[str] = None,
    **kwargs: Any,
) -> click.Command:
    """
    Create a Click command to generate shell autocompletion scripts.

    Args:
        program_name: The name of the program. If not provided, it will be inferred.
        **kwargs: Additional keyword arguments to customize the `@click.command`.

    Returns:
        A Click command to handle autocompletion generation.
    """
```

### `FileType`

```python
class FileType(click.ParamType):
    """
    Custom Click parameter type to validate file paths and extensions.

    Args:
        extensions: A list of valid file extensions (e.g., ['.json', '.txt']).
        case_sensitive: If False, extension checks will be case-insensitive.
        readable: If True, the file must be readable.
        exists: If True, the file must exist.
        resolve_path: If True, resolve the path to an absolute path.
        writable: If True, the file must be writable.
        executable: If True, the file must be executable.
    """
```

______________________________________________________________________

## Supported Shells

Currently, `click-complete` supports the following shells:

- `fish`
- `bash` (coming soon)
- `zsh` (coming soon)

______________________________________________________________________

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on [GitHub](https://github.com/xMohnad/click-complete).

______________________________________________________________________

## License

`click-complete` is licensed under the MIT License. See [MIT License](https://opensource.org/licenses/MIT) for more details.

______________________________________________________________________

## Acknowledgments

- Built on top of the amazing [Click](https://click.palletsprojects.com/) library.
- Inspired by [shellingham](https://github.com/sarugaku/shellingham) for shell detection.
