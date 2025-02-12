from typing import TYPE_CHECKING, Any, Callable, Optional, TypeVar, Union, cast

import click

from click_complete.core.parser import ClickParser
from click_complete.models import ShellType

try:
    import shellingham
except ImportError:
    shellingham = None


if TYPE_CHECKING:
    import typing_extensions as te

T = TypeVar("T")
_AnyCallable = Callable[..., Any]
_Decorator: "te.TypeAlias" = Callable[[T], T]
FC = TypeVar("FC", bound=Union[_AnyCallable, click.Command])


def get_completion(
    cli: Union[click.Group, click.Command], program_name: str, shell: str
) -> str:
    """
    Generate a shell completion script for the given CLI program.

    This function generates a completion script tailored to the specified shell type.
    Currently, only Fish shell is supported.

    Args:
        cli: The Click command or group to generate completion for.
        program_name: The name of the CLI program.
        shell: The type of shell to generate completion for (e.g., 'fish').

    Returns:
        The completion script as a string.

    Raises:
        click.UsageError: If the specified shell is not supported or not found.

    Example:
        ```python
        @click.command()
        def mycli():
            \"\"\"A sample CLI tool.\"\"\"
            click.echo("Welcome to my CLI!")

        completion_script = get_completion(mycli, "mycli", ShellType.FISH)
        click.echo(completion_script)
        ```
    """
    if not shell:
        raise click.UsageError("No shell specified. Please provide a valid shell type.")

    if shell not in ShellType.get_all_values():
        raise click.UsageError(
            f"Unsupported shell: {shell}. Supported shells are: {', '.join(ShellType.get_all_values())}"
        )

    parser = ClickParser(cli, program_name)
    if shell == ShellType.FISH:
        return parser.fish_completion
    else:
        return f"# Completion script for {shell} is not yet implemented."


def completion_option(
    *param_decls: str,
    program_name: Optional[str] = None,
    **kwargs: Any,
) -> _Decorator[FC]:
    """
    A decorator to add an option for generating shell completion scripts
    to a Click command/group.

    Parameters:
        param_decls (str): Names of the option (e.g., "--completion").
        program_name (Optional[str]): The name of the program. If not provided,
                                      it will be inferred automatically.
        kwargs (Any): Additional keyword arguments passed to `click.option`.

    Returns:
        _Decorator[FC]: A Click decorator for adding the completion option.

    Example usage:
    ```python
    import click
    from click_complete import completion_option

    @click.command()
    @completion_option()
    def mycli():
        \"\"\"A sample CLI tool.\"\"\"
        click.echo("Welcome to my CLI!")

    if __name__ == "__main__":
        mycli()
     ```
    """

    def callback(ctx: click.Context, _: click.Parameter, value: Any) -> None:
        """Callback for handling the autocomplete option."""
        if ctx.resilient_parsing:
            return

        nonlocal program_name

        if program_name is None:
            program_name = ctx.find_root().info_name

        assert program_name

        click.echo(get_completion(ctx.command, program_name, value))
        ctx.exit()

    # Set default option values
    if not param_decls:
        param_decls = ("--completion",)

    kwargs.setdefault("is_eager", True)
    kwargs.setdefault(
        "help", "Generate a shell completion script for your preferred shell."
    )

    if shellingham:
        shell, _ = shellingham.detect_shell()
        kwargs.setdefault("default", shell)

    kwargs["type"] = click.Choice(ShellType.get_all_values())
    kwargs["callback"] = callback

    return click.option(*param_decls, **kwargs)


def completion_command(
    program_name: Optional[str] = None,
    **kwargs: Any,
) -> click.Command:
    """
    Create a Click command to generate shell autocompletion scripts.

    Args:
        program_name (Optional[str]): The name of the program. If not provided,
            it will be inferred from the root context.
        **kwargs (Any): Additional keyword arguments to customize the `@click.command`.

    Returns:
        click.Command: A Click command to handle autocompletion generation.

    Raises:
        RuntimeError: If the parent context or its command is not available.

    Example:
        Add the completion command to your CLI group:
        ```python
        @click.group()
        def cli():
            pass

        cli.add_command(completion_command(program_name="my_app"))

        if __name__ == "__main__":
            cli()
        ```
    """

    if shellingham:
        shell, _ = shellingham.detect_shell()
    else:
        shell = None

    @click.command(
        **kwargs,
    )
    @click.argument(
        "shell",
        type=click.Choice(ShellType.get_all_values(), case_sensitive=False),
        default=shell,
    )
    @click.pass_context
    def completion(ctx: click.Context, shell: str) -> None:
        """
        Generate a shell completion script for your preferred shell.

        This command generates a script that enables autocompletion for this CLI tool
        in your shell. You can either load the script temporarily for the current session
        or save it permanently for future use.
        """

        if ctx.resilient_parsing:
            return

        nonlocal program_name

        if program_name is None:
            program_name = ctx.find_root().info_name

        assert program_name

        if ctx.parent is None or not hasattr(ctx.parent, "command"):
            raise RuntimeError("Parent context or command is not available.")

        click.echo(get_completion(ctx.parent.command, program_name, shell))
        ctx.exit()

    return cast(click.Command, completion)


if __name__ == "__main__":

    @click.group(context_settings={"help_option_names": ["-h", "--help"]})
    @completion_option()
    def cli():
        """Generate shell completion scripts for Click apps."""
        pass

    # Adding the completion command to the CLI
    cli.add_command(completion_command())
