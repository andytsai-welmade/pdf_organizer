from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class PageState:
    items: list[tuple[str, int]] = field(default_factory=list)
    month: int = field(default_factory=lambda: datetime.now().month)
    year: int = field(default_factory=lambda: datetime.now().year)
    saved_path: str | None = None


