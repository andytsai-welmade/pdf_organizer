"""PySide6 desktop window and user interaction."""
from __future__ import annotations
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QComboBox, QFileDialog, QFormLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QMainWindow, QMessageBox, QPushButton,
    QScrollArea, QSpinBox, QSplitter, QVBoxLayout, QWidget,
)
from ui.excel_config_dialog import ExcelConfigDialog
from modules.filename_generator import MONTHS, make_filename
from modules.page_state import PageState
from modules.pdf_handler import open_document, render_page, export_page

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PDF Organizer — Version 1')
        self.resize(1200, 780)
        self.document = None
        self.pdf_path = None
        self.output_dir = None
        self.products: dict[str, str] = {}
        self.states: list[PageState] = []
        self.index = 0
        self.zoom = 1.25
        self._build_ui()
        self._update_controls()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)     # -> the vertical layout for overall UI
        toolbar = QHBoxLayout()         # -> the horizontal bar layout for buttons

        # Create push buttons in the UI
        self.pdf_button = QPushButton('1. Open scanned PDF')
        self.pdf_button.clicked.connect(self.open_pdf)
        
        self.excel_button = QPushButton('2. Configure product Excel')
        self.excel_button.clicked.connect(self.open_excel)

        self.folder_button = QPushButton('3. Choose output folder')
        self.folder_button.clicked.connect(self.choose_output)

        # Arrange buttons layout on the top
        for b in (self.pdf_button, self.excel_button, self.folder_button):
            toolbar.addWidget(b)
        root.addLayout(toolbar)

        # Show the status using label
        self.status = QLabel('Steps to begin: Open a PDF -> Load Excel & configure the excel format -> Select an output folder')
        self.status.setWordWrap(True)
        root.addWidget(self.status)

        '''
        Split the remaining layout for preview (left) and function page (right)
        '''
        splitter = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(splitter, 1)

        # Left preview layout
        left = QWidget()
        lv = QVBoxLayout(left)
        zoomrow = QHBoxLayout()
        self.page_label = QLabel('No PDF loaded')
        zoomrow.addWidget(self.page_label, 1)
        minus = QPushButton('−')
        plus = QPushButton('+')
        minus.clicked.connect(lambda: self.change_zoom(0.8))
        plus.clicked.connect(lambda: self.change_zoom(1.25))
        zoomrow.addWidget(minus)
        zoomrow.addWidget(plus)
        lv.addLayout(zoomrow)
        self.preview = QLabel('Open a PDF to see a page preview')
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(False)
        self.scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll.setWidget(self.preview)
        lv.addWidget(self.scroll, 1)
        splitter.addWidget(left)

        # Right function layout
        right = QWidget()
        rv = QVBoxLayout(right)
        group = QGroupBox('Products on current page')
        gv = QVBoxLayout(group)
        self.search = QLineEdit()
        self.search.setPlaceholderText('Search product code or name...')
        self.search.textChanged.connect(self.filter_products)
        gv.addWidget(self.search)
        self.product_combo = QComboBox()
        gv.addWidget(self.product_combo)
        qtyrow = QHBoxLayout()
        self.qty = QSpinBox()
        self.qty.setRange(1, 99999)
        self.qty.setValue(1)
        add = QPushButton('Add product')
        add.clicked.connect(self.add_product)
        qtyrow.addWidget(QLabel('Quantity'))
        qtyrow.addWidget(self.qty)
        qtyrow.addWidget(add)
        gv.addLayout(qtyrow)
        self.item_list = QListWidget()
        gv.addWidget(self.item_list)
        remove = QPushButton('Remove selected product')
        remove.clicked.connect(self.remove_product)
        gv.addWidget(remove)
        rv.addWidget(group, 1)

        # "Document date" group layout
        date_group = QGroupBox('Document date')
        date_form = QFormLayout(date_group)
        self.month = QComboBox()
        self.month.addItems(MONTHS)
        self.year = QSpinBox()
        self.year.setRange(1900, 3000)
        self.month.currentIndexChanged.connect(self.date_changed)
        self.year.valueChanged.connect(self.date_changed)
        date_form.addRow('Month', self.month)
        date_form.addRow('Year', self.year)
        rv.addWidget(date_group)

        # "Output filename preview" layout
        rv.addWidget(QLabel('Output filename preview:'))
        self.filename_label = QLabel('—')
        self.filename_label.setWordWrap(True)
        self.filename_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        rv.addWidget(self.filename_label)
        self.saved_label = QLabel('')
        self.saved_label.setWordWrap(True)
        rv.addWidget(self.saved_label)
        nav = QHBoxLayout()
        self.prev = QPushButton('← Previous')
        self.next = QPushButton('Save and Continue →')
        self.prev.clicked.connect(self.previous)
        self.next.clicked.connect(self.save_and_continue)
        nav.addWidget(self.prev)
        nav.addWidget(self.next)
        rv.addLayout(nav)
        splitter.addWidget(right)
        splitter.setSizes([740, 460])

    def open_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Open scanned PDF', '', 'PDF files (*.pdf)')
        if not path:
            return
        try:
            doc = open_document(path)
            if doc.page_count == 0 or doc.needs_pass:
                raise ValueError('The PDF is empty or password protected.')
        except Exception as exc:
            QMessageBox.critical(self, 'Cannot open PDF', str(exc))
            return
        if self.document:
            self.document.close()
        self.document = doc
        self.pdf_path = path
        self.states = [PageState() for _ in range(doc.page_count)]
        self.index = 0
        self._load_page()

    def open_excel(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Open product database', '', 'Excel files (*.xlsx)')
        if not path:
            return
        try:
            dialog = ExcelConfigDialog(path, self)
            if dialog.exec() != dialog.DialogCode.Accepted:
                return
            self.products = dialog.products
            self.search.clear()
            self.filter_products()
            self._refresh_items()
        except Exception as exc:
            QMessageBox.critical(self, 'Cannot configure Excel', str(exc))

    def choose_output(self):
        path = QFileDialog.getExistingDirectory(self, 'Choose output folder')
        if path:
            self.output_dir = Path(path)
            self._update_controls()

    def filter_products(self, *_):
        current = self.product_combo.currentData()
        term = self.search.text().strip().casefold()
        self.product_combo.clear()
        for code, name in self.products.items():
            if term in code.casefold() or term in name.casefold():
                self.product_combo.addItem(f'{code} — {name}', code)
        pos = self.product_combo.findData(current)
        if pos >= 0:
            self.product_combo.setCurrentIndex(pos)

    def add_product(self):
        if not self.states:
            return
        code = self.product_combo.currentData()
        if not code:
            QMessageBox.warning(self, 'No matching product', 'Select a product from the Excel database.')
            return
        state = self.states[self.index]
        qty = self.qty.value()
        for i, (existing, amount) in enumerate(state.items):
            if existing == code:
                state.items[i] = (code, amount + qty)
                break
        else:
            state.items.append((code, qty))
        self._refresh_items()

    def remove_product(self):
        if not self.states:
            return
        row = self.item_list.currentRow()
        if row >= 0:
            self.states[self.index].items.pop(row)
            self._refresh_items()

    def date_changed(self, *_):
        if self.states:
            state = self.states[self.index]
            state.month = self.month.currentIndex() + 1
            state.year = self.year.value()
            self._update_controls()

    def _refresh_items(self):
        self.item_list.clear()
        if self.states:
            for code, qty in self.states[self.index].items:
                self.item_list.addItem(f'{code} — {self.products.get(code, "Unknown product")}  × {qty}')
        self._update_controls()

    def _load_page(self):
        if not self.document:
            return
        state = self.states[self.index]
        self.month.blockSignals(True)
        self.year.blockSignals(True)
        self.month.setCurrentIndex(state.month - 1)
        self.year.setValue(state.year)
        self.month.blockSignals(False)
        self.year.blockSignals(False)
        self._refresh_items()
        self.render_page()

    def render_page(self):
        if not self.document:
            return
        pix = render_page(self.document, self.index, self.zoom)
        img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888).copy()
        self.preview.setPixmap(QPixmap.fromImage(img))
        self.preview.resize(pix.width, pix.height)
        self._update_controls()

    def change_zoom(self, factor):
        self.zoom = max(0.4, min(3.0, self.zoom * factor))
        self.render_page()

    def _update_controls(self):
        ready = bool(self.document and self.products and self.output_dir)
        has_doc = bool(self.document)
        self.prev.setEnabled(has_doc and self.index > 0)
        self.next.setEnabled(ready)
        if not has_doc:
            self.filename_label.setText('—')
            self.saved_label.setText('')
            return
        state = self.states[self.index]
        self.page_label.setText(f'Page {self.index + 1} / {len(self.states)}  |  Zoom {self.zoom:.0%}')
        try:
            name = make_filename(state.items, state.month, state.year)
        except ValueError:
            name = '(Add at least one product to generate a filename)'
        self.filename_label.setText(name)
        self.saved_label.setText(f'Previously saved: {state.saved_path}' if state.saved_path else 'Not yet saved')
        saved_count = sum(bool(s.saved_path) for s in self.states)
        self.status.setText(f'{saved_count}/{len(self.states)} pages saved  |  Excel products: {len(self.products)}  |  Output: {self.output_dir or "Not selected"}')
        self.next.setText('Save final page' if self.index == len(self.states) - 1 else 'Save & Continue →')

    def previous(self):
        if self.index > 0:
            self.index -= 1
            self._load_page()

    def save_and_continue(self):
        if not (self.document and self.output_dir and self.products):
            return
        state = self.states[self.index]
        try:
            for code, _ in state.items:
                if code not in self.products:
                    raise ValueError(f'Product {code} is missing from the loaded Excel file.')
            name = make_filename(state.items, state.month, state.year)
        except ValueError as exc:
            QMessageBox.warning(self, 'Invalid filename', str(exc))
            return
        target = self.output_dir / name
        old = Path(state.saved_path) if state.saved_path else None
        if target.exists():
            # Never overwrite another page's output or an unrelated file.
            owned_by_other = any(s.saved_path and Path(s.saved_path) == target for i, s in enumerate(self.states) if i != self.index)
            if owned_by_other or old != target:
                QMessageBox.warning(self, 'Filename already exists', f'{target.name}\n\nChange the product list/date or select another output folder. No file was overwritten.')
                return
            choice = QMessageBox.question(self, 'Replace your saved page?', f'Re-export page {self.index + 1} to:\n{target.name}?')
            if choice != QMessageBox.StandardButton.Yes:
                return
        try:
            export_page(self.document, self.index, target)
        except Exception as exc:
            QMessageBox.critical(self, 'Export failed', str(exc))
            return
        state.saved_path = str(target)
        if old and old != target and old.exists():
            # Do not silently delete the old export after renaming; tell user instead.
            QMessageBox.information(self, 'New filename saved', f'New file saved. Previous export still exists:\n{old.name}\n\nDelete the old file manually if no longer needed.')
        if self.index < len(self.states) - 1:
            self.index += 1
            self._load_page()
        else:
            self._update_controls()
            QMessageBox.information(self, 'Finished', f'Final page saved.\n\n{sum(bool(s.saved_path) for s in self.states)} of {len(self.states)} pages have been exported.\n\nOutput folder:\n{self.output_dir}')

    def closeEvent(self, event):
        if self.document:
            self.document.close()
        super().closeEvent(event)

