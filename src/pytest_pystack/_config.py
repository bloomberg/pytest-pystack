import dataclasses
from typing import Optional


@dataclasses.dataclass
class PystackConfig:
    timeout: float
    pystack_path: str
    output_file: Optional[str] = None
    print_stderr: bool = True
    pystack_args: Optional[str] = None
