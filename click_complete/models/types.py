from pathlib import Path
from typing import List, Optional

import click


class FileType(click.ParamType):
    """Custom Click parameter type to validate file paths and extensions."""

    name = "file"

    def __init__(
        self,
        extensions: List[str],
        case_sensitive: bool = True,
        readable: bool = True,
        exists: bool = True,
        resolve_path: bool = False,
        writable: bool = False,
        executable: bool = False,
    ):
        """
        Initialize the FileType validator.

        Args:
            extensions: A list of valid file extensions (e.g., ['.json', '.txt']).
            case_sensitive: If False, extension checks will be case-insensitive.
            readable: If True, the file must be readable.
            exists: If True, the file must exist.
            resolve_path: If True, resolve the path to an absolute path.
            writable: If True, the file must be writable.
            executable: If True, the file must be executable.
        """
        if not extensions:
            raise ValueError("At least one file extension must be provided.")

        self.extensions = extensions
        self.case_sensitive = case_sensitive
        self.path_type = click.Path(
            file_okay=True,
            dir_okay=False,
            exists=exists,
            readable=readable,
            writable=writable,
            executable=executable,
            resolve_path=resolve_path,
        )

    def convert(
        self, value: str, param: Optional[click.Parameter], ctx: Optional[click.Context]
    ) -> Path:
        """
        Validate the file path and its extension.

        Args:
            value: The file path provided by the user.
            param: The Click parameter object.
            ctx: The Click context object.

        Returns:
            The validated file path as a Path object.

        Raises:
            click.BadParameter: If the file does not exist, is not readable, or has an invalid extension.
        """
        # Use the internal click.Path type to validate the basic file properties
        path_str = self.path_type.convert(value, param, ctx)
        path = Path(str(path_str))

        # Check if the file has a valid extension
        if self.case_sensitive:
            valid_extension = any(path.name.endswith(ext) for ext in self.extensions)
        else:
            valid_extension = any(
                path.name.lower().endswith(ext.lower()) for ext in self.extensions
            )

        if not valid_extension:
            case_msg = " (case-insensitive)" if not self.case_sensitive else ""
            raise click.BadParameter(
                f"File '{path.name}' must have one of the following extensions{case_msg}: {', '.join(self.extensions)}"
            )

        return path
