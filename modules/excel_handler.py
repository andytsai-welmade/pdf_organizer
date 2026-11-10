"""Project-specific Excel worksheet and WBS mapping."""
from __future__ import annotations
import re
from openpyxl import load_workbook
from openpyxl.utils.cell import range_boundaries, get_column_letter
from .validators import INVALID_FILENAME


def list_sheets(path: str) -> list[str]:
    wb = load_workbook(path, read_only=True, data_only=True)
    try:
        return list(wb.sheetnames)
    finally:
        wb.close()


def parse_single_column_range(address: str) -> tuple[int, int, int]:
    address = address.strip().upper().replace('$', '')
    if not re.fullmatch(r'[A-Z]+[1-9][0-9]*:[A-Z]+[1-9][0-9]*', address):
        raise ValueError('Use a single-column range such as A7:A46.')
    c1, r1, c2, r2 = range_boundaries(address)
    if c1 != c2 or r1 > r2:
        raise ValueError('Range must cover one column, from top to bottom.')
    return c1, r1, r2


def _code_from_cell(cell) -> str:
    value = cell.value
    if value is None or str(value).strip() == '':
        return ''
    if isinstance(value, bool):
        raise ValueError(f'Invalid boolean WBS code in {cell.coordinate}.')
    if isinstance(value, (int, float)):
        fmt = cell.number_format or ''
        # Excel numeric display formats like 0.00 preserve trailing zeros.
        if re.fullmatch(r'0(?:\.0+)?', fmt):
            decimals = len(fmt.split('.')[1]) if '.' in fmt else 0
            return f'{value:.{decimals}f}'
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)
    return str(value).strip()


def read_products(path: str, sheet_name: str | None = None,
                  wbs_range: str = 'A2:A100',
                  description_range: str = 'B2:B100') -> dict[str, str]:
    c1, r1, r2 = parse_single_column_range(wbs_range)
    c2, s1, s2 = parse_single_column_range(description_range)
    if r2 - r1 != s2 - s1:
        raise ValueError('WBS and description ranges must contain the same number of rows.')
    wb = load_workbook(path, read_only=True, data_only=True)
    try:
        if sheet_name and sheet_name not in wb.sheetnames:
            raise ValueError(f'Worksheet not found: {sheet_name}')
        ws = wb[sheet_name] if sheet_name else wb.active
        products = {}
        for offset in range(r2 - r1 + 1):
            code_cell = ws.cell(row=r1 + offset, column=c1)
            code = _code_from_cell(code_cell)
            description = ws.cell(row=s1 + offset, column=c2).value
            if not code:
                if description is not None and str(description).strip():
                    raise ValueError(f'Description has no WBS code at {code_cell.coordinate}.')
                continue
            if INVALID_FILENAME.search(code) or code.endswith(('.', ' ')):
                raise ValueError(f'Invalid WBS code at {code_cell.coordinate}: {code!r}')
            if code in products:
                raise ValueError(f'Duplicate WBS code: {code} ({code_cell.coordinate})')
            if description is None or not str(description).strip():
                raise ValueError(f'Missing description for {code} at {code_cell.coordinate}.')
            products[code] = str(description).strip()
        if not products:
            raise ValueError('No WBS items found in the selected ranges.')
        return products
    finally:
        wb.close()


def worksheet_preview(path: str, sheet_name: str, max_rows: int = 250,
                      max_cols: int = 24) -> tuple[list[list[str]], bool]:
    wb = load_workbook(path, read_only=True, data_only=True)
    try:
        ws = wb[sheet_name]
        rows = []
        for row in ws.iter_rows(min_row=1, max_row=min(ws.max_row, max_rows),
                                max_col=min(ws.max_column, max_cols)):
            rows.append([_code_from_cell(c) if c.value is not None else '' for c in row])
        truncated = ws.max_row > max_rows or ws.max_column > max_cols
        return rows, truncated
    finally:
        wb.close()
