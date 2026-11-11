from __future__ import annotations
from .validators import INVALID_FILENAME

MONTHS_ABBR = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

def make_filename(items: list[tuple[str, int]], month: int, year: int) -> str:
    # Empty filename
    if not items:
        raise ValueError('Add at least one product.')
    
    # if not (1 <= month <= 12 and 2000 <= year <= 2099):
    #     raise ValueError('Choose a valid month and year (2000–2099).')
    if not (1 <= month <= 12):
        raise ValueError('Choose a valid month (1–12).')

    # Duplicate item codes
    if len({code for code, _ in items}) != len(items):
        raise ValueError('A product code cannot appear twice; combine quantities.')
    
    # Check for invalid filename and invalid item numbers
    '''
    TODO: check the item quantity in the excel
    '''
    for code, quantity in items:
        if not code or INVALID_FILENAME.search(code) or code.endswith(('.', ' ')):
            raise ValueError(f'Invalid product code: {code!r}')
        if not isinstance(quantity, int) or quantity < 1:
            raise ValueError('All quantities must be positive integers.')

    
    # return ', '.join(f'{code}x{qty}' for code, qty in items) + f', {MONTHS[month - 1]}.{year % 100:02d}.pdf'
    return ', '.join(f'{code}x{qty}' for code, qty in items) + f', {MONTHS_ABBR[month - 1]} {year}.pdf'


