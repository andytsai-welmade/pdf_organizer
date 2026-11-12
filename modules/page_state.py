from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class PageState:
    items: list[tuple[str, int]] = field(default_factory=list)

    # Make the month and year as it is when previous page is saved
    month: int = field(default_factory=lambda: datetime.now().month)
    year: int = field(default_factory=lambda: datetime.now().year)
    
    saved_path: str | None = None

    custom_filename: str | None = None


