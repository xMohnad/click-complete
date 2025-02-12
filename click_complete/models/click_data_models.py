from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Option:
    short: Optional[str]
    long: Optional[str]
    secondary_opts: List[str]
    help: str
    type: Optional[Any] = None


@dataclass
class Argument:
    name: str | None
    help: str
    type: Optional[Any] = None


@dataclass
class CommandData:
    name: str
    help: str
    commands: Dict[str, "CommandData"] = field(default_factory=dict)
    options: List[Option] = field(default_factory=list)
    arguments: List[Argument] = field(default_factory=list)
