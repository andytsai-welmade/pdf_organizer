from __future__ import annotations
from .validators import INVALID_FILENAME

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def make_filename(items: list[tuple[str, int]], month: int, year: int) -> str:
    if not items:
        raise ValueError('Add at least one product.')
    if not (1 <= month <= 12 and 2000 <= year <= 2099):
        raise ValueError('Choose a valid month and year (2000–2099).')
    if len({code for code, _ in items}) != len(items):
        raise ValueError('A product code cannot appear twice; combine quantities.')
    for code, quantity in items:
        if not code or INVALID_FILENAME.search(code) or code.endswith(('.', ' ')):
            raise ValueError(f'Invalid product code: {code!r}')
        if not isinstance(quantity, int) or quantity < 1:
            raise ValueError('All quantities must be positive integers.')
    # return ', '.join(f'{code}x{qty}' for code, qty in items) + f', {MONTHS[month - 1]}.{year % 100:02d}.pdf'
    return ', '.join(f'{code}x{qty}' for code, qty in items) + f', {MONTHS[month - 1]} {year}.pdf'


