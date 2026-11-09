from __future__ import annotations
from openpyxl import load_workbook
from .validators import INVALID_FILENAME

def read_products(path: str) -> dict[str, str]:
    """Read first worksheet: column A = code, column B = product name.

    Header row is optional; empty rows are ignored. Codes should be stored as
    text in Excel to preserve exact formatting (e.g., 1.10 vs 1.1).
    """
    book = load_workbook(path, read_only=True, data_only=True)
    try:
        sheet = book.active
        products = {}
        for row in sheet.iter_rows(min_row=1, max_col=2, values_only=True):
            code, name = row
            if code is None or str(code).strip() == '':
                continue
            code = str(code).strip()
            if code.lower() in {'code', 'product code', 'item code'}:
                continue
            if INVALID_FILENAME.search(code) or code.endswith(('.', ' ')):
                raise ValueError(f'Invalid product code for a filename: {code!r}')
            if code in products:
                raise ValueError(f'Duplicate product code in Excel: {code}')
            products[code] = str(name).strip() if name is not None else code
        if not products:
            raise ValueError('No product codes found in columns A and B.')
        return products
    finally:
        book.close()


