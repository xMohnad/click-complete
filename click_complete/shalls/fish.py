import shutil
from pathlib import Path
from typing import Any, Optional

from click.types import INT, Choice

from click_complete.models import CommandData, Option
from click_complete.models.types import FileType


class FishCompletionGenerator:
    def __init__(self, data: CommandData):
        self._data = data
        # from rich import print
        #
        # print(data)
        #

    @property
    def completion_code(self) -> str:
        """Generate and return the fish completion script."""
        return self._generate_fish_completion(self._data)

    def _generate_fish_completion(self, data: CommandData) -> str:
        """Generate fish completion script from CommandData."""
        completion_script = []

        # Add header
        completion_script.append(f"# fish completion for {data.name}\n")
        completion_script.append(f"complete -c {data.name} -f\n")

        # Add commands
        for command_name, command_data in data.commands.items():
            completion_script.append(
                f"complete -c {data.name} -n '__fish_use_subcommand' "
                f"-a {command_name} "
                + (f'-d "{command_data.help}"' if command_data.help else "")
            )

            # Add command-specific options
            completion_script.extend(
                self._generate_option_completion(data.name, option, command_name)
                for option in command_data.options
            )

            # Add command-specific arguments
            for argument in command_data.arguments:
                completion_line = [
                    f"complete -c {data.name}",
                    f"-n '__fish_seen_subcommand_from {command_name}'",
                    f'-d "{argument.help}"' if argument.help else "",
                ]

                # Handle type-specific completions
                if argument.type:
                    completion_line.append(self._handle_type(argument.type))

                # Join the completion line into a single string
                completion_script.append(" ".join(completion_line))

        # Add global options
        completion_script.extend(
            self._generate_option_completion(data.name, option)
            for option in data.options
        )

        # Join the list into a single string
        return "\n".join(completion_script)

    def _generate_option_completion(
        self, command_name: str, option: Option, subcommand: Optional[str] = None
    ) -> str:
        """Generate fish completion for an option."""
        completion_line = [f"complete -c {command_name}"]

        # Add subcommand condition if applicable
        if subcommand:
            completion_line.append(f"-n '__fish_seen_subcommand_from {subcommand}'")
        else:
            completion_line.append("-n '__fish_use_subcommand'")

        # Add short and long options
        if option.short:
            completion_line.append(f"-s {option.short.lstrip('-')}")
        if option.long:
            completion_line.append(f"-l {option.long.lstrip('--')}")
            if option.secondary_opts:
                completion_line.extend(
                    f"-l {opt.lstrip('--')}" for opt in option.secondary_opts
                )

        # Add description
        if option.help:
            completion_line.append(f'-d "{option.help}"')

        # Handle type-specific completions
        if option.type:
            completion_line.append(self._handle_type(option.type))

        return " ".join(completion_line)

    def _handle_type(self, type_obj: Any) -> str:
        """Generate type-specific completion arguments."""
        if isinstance(type_obj, Choice):
            # Ensure choices are cleanly joined
            choices = " ".join(map(str, type_obj.choices))
            return f'-x -a "{choices}"'
        elif isinstance(type_obj, Path):
            # Use fish's built-in path completion
            return '-x -a "(__fish_complete_path)"'
        elif type_obj is INT:
            # Improved number completion
            return '-x -a "(for i in (seq 1 100); echo $i\\t\\"Number $i\\"; end)"'
        elif isinstance(type_obj, FileType):
            return '-x -a "{}"'.format(self._generate_find_command(type_obj))
        else:
            # Default behavior for unknown types
            return ""

    def _generate_find_command(self, type_obj: FileType) -> str:
        """
        Generate a Fish shell command to filter files by extensions using `find`.

        Args:
            extensions (list[str]): List of file extensions to filter by.

        Returns:
            str: The generated `find` command as a string.
        """

        if not type_obj.extensions:
            return ""

        if not shutil.which("fd"):
            name = "-name" if type_obj.case_sensitive else "-iname"

            # Create the extensions string for the `find` command
            extensions_str = " ".join(
                f"{name} '*{ext}'" if i == 0 else f"-o {name} '*{ext}'"
                for i, ext in enumerate(type_obj.extensions)
            )

            # Return the full `find` command
            return f'(find . -type f \\( {extensions_str} \\) -printf "%P\\n")'

        # Create the extensions string for the `fd` command
        extensions_str = " ".join(f"-e {ext}" for ext in type_obj.extensions)

        return f"(fd {extensions_str}  --type f {'' if type_obj.case_sensitive else '--ignore-case'})"
