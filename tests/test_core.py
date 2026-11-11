import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
from openpyxl import Workbook
from modules.filename_generator import make_filename
from modules.excel_handler import read_products


class TestCore(unittest.TestCase):
    def test_filename(self):
        self.assertEqual(make_filename([('1.11', 1), ('2.3', 2)], 10, 2026), '1.11x1, 2.3x2, Oct 2026.pdf')

    def test_duplicate_codes_rejected(self):
        with self.assertRaises(ValueError):
            make_filename([('1.1', 1), ('1.1', 2)], 10, 2026)

    def test_empty_rejected(self):
        with self.assertRaises(ValueError):
            make_filename([], 10, 2026)

    def test_excel(self):
        with TemporaryDirectory() as temp:
            p = Path(temp) / 'products.xlsx'
            wb = Workbook()
            ws = wb.active
            ws.append(['Product Code', 'Product Name'])
            ws.append(['1.11', 'Product 11'])
            ws.append(['2.3', 'Product 23'])
            wb.save(p)
            self.assertEqual(read_products(str(p)), {'1.11': 'Product 11', '2.3': 'Product 23'})


if __name__ == '__main__':
    unittest.main()
