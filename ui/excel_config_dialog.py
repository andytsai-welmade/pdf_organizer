"""Select a worksheet and two aligned single-column ranges, manually or visually."""
from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QComboBox, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QAbstractItemView, QMessageBox, QDialogButtonBox, QGroupBox)
from openpyxl.utils.cell import get_column_letter
from modules.excel_handler import list_sheets, read_products, worksheet_preview


class ExcelConfigDialog(QDialog):
    def __init__(self, path: str, parent=None):
        super().__init__(parent)
        self.path = path
        self.products = {}
        self.setWindowTitle('Configure Excel WBS mapping')
        self.resize(1050, 760)
        root = QVBoxLayout(self)
        root.addWidget(QLabel('Choose worksheet, then type ranges or select cells in the grid below.'))
        form = QFormLayout()
        self.sheet = QComboBox()
        self.sheet.addItems(list_sheets(path))
        self.sheet.currentTextChanged.connect(self.reload_sheet)
        form.addRow('Worksheet:', self.sheet)
        self.wbs = QLineEdit('A7:A46')
        self.desc = QLineEdit('B7:B46')
        form.addRow('WBS item range:', self.wbs)
        form.addRow('Description range:', self.desc)
        root.addLayout(form)
        self.table = QTableWidget()
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        root.addWidget(self.table, 3)
        selection = QHBoxLayout()
        wbs_btn = QPushButton('Use selected cells as WBS range')
        desc_btn = QPushButton('Use selected cells as description range')
        wbs_btn.clicked.connect(lambda: self.set_from_selection(self.wbs))
        desc_btn.clicked.connect(lambda: self.set_from_selection(self.desc))
        selection.addWidget(wbs_btn)
        selection.addWidget(desc_btn)
        root.addLayout(selection)
        self.note = QLabel('')
        self.note.setWordWrap(True)
        root.addWidget(self.note)
        preview_group = QGroupBox('Mapped WBS item preview')
        preview_layout = QVBoxLayout(preview_group)
        self.preview = QTableWidget(0, 2)
        self.preview.setHorizontalHeaderLabels(['WBS item', 'Description'])
        self.preview.horizontalHeader().setStretchLastSection(True)
        self.preview.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        preview_layout.addWidget(self.preview)
        root.addWidget(preview_group, 2)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText('Use this mapping')
        buttons.accepted.connect(self.accept_mapping)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)
        test = QPushButton('Validate ranges and preview mapping')
        test.clicked.connect(self.validate_mapping)
        root.insertWidget(root.count() - 1, test)
        self.reload_sheet()

    def reload_sheet(self, *_):
        try:
            rows, truncated = worksheet_preview(self.path, self.sheet.currentText())
            self.table.setRowCount(len(rows))
            self.table.setColumnCount(max((len(r) for r in rows), default=0))
            self.table.setHorizontalHeaderLabels([get_column_letter(i + 1) for i in range(self.table.columnCount())])
            self.table.setVerticalHeaderLabels([str(i + 1) for i in range(len(rows))])
            for i, row in enumerate(rows):
                for j, value in enumerate(row):
                    cell = QTableWidgetItem(value)
                    cell.setFlags(cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.table.setItem(i, j, cell)
            self.note.setText('Preview limited to first 250 rows / 24 columns; type ranges manually for cells outside the preview.' if truncated else 'Select a contiguous vertical group of cells (click first cell, Shift-click last).')
            self.preview.setRowCount(0)
        except Exception as exc:
            QMessageBox.critical(self, 'Cannot preview worksheet', str(exc))

    def set_from_selection(self, target: QLineEdit):
        indexes = self.table.selectedIndexes()
        if not indexes:
            QMessageBox.warning(self, 'No cells selected', 'Select the cells in one column first.')
            return
        columns = {x.column() for x in indexes}
        rows = {x.row() for x in indexes}
        if len(columns) != 1 or len(indexes) != max(rows) - min(rows) + 1:
            QMessageBox.warning(self, 'Invalid selection', 'Select one contiguous vertical range in a single column.')
            return
        col = get_column_letter(next(iter(columns)) + 1)
        target.setText(f'{col}{min(rows)+1}:{col}{max(rows)+1}')

    def validate_mapping(self) -> bool:
        try:
            products = read_products(self.path, self.sheet.currentText(), self.wbs.text(), self.desc.text())
        except Exception as exc:
            self.products = {}
            self.preview.setRowCount(0)
            QMessageBox.warning(self, 'Invalid Excel mapping', str(exc))
            return False
        self.products = products
        self.preview.setRowCount(len(products))
        for i, (code, name) in enumerate(products.items()):
            self.preview.setItem(i, 0, QTableWidgetItem(code))
            self.preview.setItem(i, 1, QTableWidgetItem(name))
        self.note.setText(f'Validated {len(products)} WBS items. Check the mapping before continuing.')
        return True

    def accept_mapping(self):
        if self.validate_mapping():
            self.accept()
