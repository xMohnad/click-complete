from __future__ import annotations

from typing import Optional

import click

from click_complete.models import Argument, CommandData, Option
from click_complete.shalls.fish import FishCompletionGenerator


class ClickParser:
    def __init__(self, cli: click.Group | click.Command, name: Optional[str] = None):
        self.help_option_names = None
        self._data = self.extract_click_commands(cli, name=name or cli.name or "")

    @property
    def commands(self) -> CommandData:
        return self._data

    @property
    def fish_completion(self) -> str:
        fish_completion = FishCompletionGenerator(self.commands)
        return fish_completion.completion_code

    @staticmethod
    def _is_short_option(option: str) -> bool:
        """Check if the option is a short option (e.g., '-h')."""
        return (
            option.startswith("-") and len(option) == 2 and not option.startswith("--")
        )

    @staticmethod
    def _is_long_option(option: str) -> bool:
        """Check if the option is a long option (e.g., '--help')."""
        return option.startswith("--")

    def _extract_option_names(
        self, opts: list[str]
    ) -> tuple[Optional[str], Optional[str]]:
        """Extract short and long option names from a list of Click options."""
        short_opt = next((opt for opt in opts if self._is_short_option(opt)), None)
        long_opt = next((opt for opt in opts if self._is_long_option(opt)), None)
        return short_opt, long_opt

    def extract_click_commands(
        self, cli: click.Group | click.Command, name: str
    ) -> CommandData:
        """Extract commands, options, and arguments from a Click group or command."""
        data = CommandData(
            name=name,
            help=cli.help.strip().split("\n")[0].strip() if cli.help else "",
        )

        # Add help options for the current command
        help_option_names = cli.context_settings.get("help_option_names")
        if not self.help_option_names:
            self.help_option_names = help_option_names
            if not self.help_option_names:
                self.help_option_names = ["--help"]

        if cli.add_help_option:
            # Help option is disabled when context setting is None
            short_help, long_help = self._extract_option_names(self.help_option_names)
            data.options.append(
                Option(
                    short=short_help,
                    long=long_help,
                    secondary_opts=[],
                    help="Show this message and exit.",
                    type=None,
                )
            )

        # Extract options and arguments
        for param in cli.params:
            if getattr(param, "hidden", False):
                continue  # Skip hidden parameters

            if isinstance(param, click.Option):
                short_opt, long_opt = self._extract_option_names(param.opts)
                data.options.append(
                    Option(
                        short=short_opt,
                        long=long_opt,
                        secondary_opts=param.secondary_opts,
                        help=param.help or "",
                        type=param.type,
                    )
                )
            elif isinstance(param, click.Argument):
                data.arguments.append(
                    Argument(
                        name=param.name,
                        help="",
                        type=param.type,
                    )
                )

        # Extract subcommands if it's a group
        if isinstance(cli, click.Group):
            for subcmd_name, subcmd in cli.commands.items():
                if getattr(subcmd, "hidden", False):
                    continue  # Skip hidden subcommands
                data.commands[subcmd_name] = self.extract_click_commands(
                    subcmd,
                    subcmd.name
                    or subcmd_name,  # Fallback to subcmd_name if subcmd.name is None
                )

        return data
