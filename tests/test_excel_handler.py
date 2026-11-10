import tempfile
import unittest
from pathlib import Path
from openpyxl import Workbook
from modules.excel_handler import read_products, parse_single_column_range

class ExcelMappingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.tmp.name) / 'sample.xlsx')
        wb = Workbook()
        ws = wb.active
        ws.title = 'Project WBS'
        ws['A7'] = '1.1'; ws['B7'] = 'Calibration'
        ws['A8'] = 4.1; ws['A8'].number_format = '0.00'; ws['B8'] = '64CH maintenance'
        ws['A9'] = '4.12'; ws['B9'] = 'Sampling'
        wb.save(self.path)
    def tearDown(self):
        self.tmp.cleanup()
    def test_mapping(self):
        result = read_products(self.path, 'Project WBS', 'A7:A9', 'B7:B9')
        self.assertEqual(result, {'1.1':'Calibration','4.10':'64CH maintenance','4.12':'Sampling'})
    def test_mismatched_ranges(self):
        with self.assertRaisesRegex(ValueError, 'same number'):
            read_products(self.path, 'Project WBS', 'A7:A9', 'B7:B8')
    def test_multicolumn_rejected(self):
        with self.assertRaises(ValueError):
            parse_single_column_range('A7:B9')
    def test_duplicate(self):
        wb = Workbook(); ws = wb.active
        ws['A7']='1.1'; ws['B7']='First'
        ws['A8']='1.1'; ws['B8']='Second'
        wb.save(self.path)
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            read_products(self.path, ws.title, 'A7:A8', 'B7:B8')

if __name__ == '__main__':
    unittest.main()
