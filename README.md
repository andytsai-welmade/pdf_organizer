# PDF Organizer V1 — Modular Python Desktop Application

[![PyPI Python Version](https://img.shields.io/pypi/pyversions/3.14.10)](https://www.python.org/downloads/)


One scanned PDF page becomes one output PDF, named from an Excel product database.

## Project layout

```text
PDF_Organizer_V1_Modular/
├── main.py                    # Application entry point
│
├── modules/
│   ├── excel_handler.py       # Read Excel product database
│   ├── pdf_handler.py         # Open, preview, export PDF pages
│   ├── filename_generator.py  # Filename rules and date formatting
│   ├── validators.py          # Filename-safe product codes
│   └── page_state.py          # Per-page selections and saved path
│
├── ui/
│   └── main_window.py         # PySide6 widgets and interactions
│
├── tests/
│   ├── test_core.py           # Filename tests
│   └── test_excel_handler.py  # Excel handler tests
│
├── data/                      # Put your Excel file here (optional)
├── output/                    # Optional export folder
├── requirements.txt
└── build_windows.bat          # Build a Windows executable
```


### Build on an approved Windows computer

<!-- > TODO: Create an .exe file to execute this project -->
Add the package into `:nas\Engineer\AMC maintenace`

## Run source code (on a computer with Python)

- Run with Python:
```powershell
python -m pip install -r requirements.txt
python main.py
```

- Run from virtual env:
```powershell
.venv\Scripts\python.exe .\main.py
```


### Run tests
- Run with python:

```powershell
python -m unittest discover -s tests -v
```

### Export project to .exe file
```powershell
python -m PyInstaller --noconfirm --clean --onedir --windowed --name PDF_Organizer main.py
```
The exported file can be find in `.\dist\PDF_Orginizer\PDF_Orginizer.exe`

## Excel format

Use the first worksheet with **column A = Product Code** and **column B = Product Name**. A header is optional. Set column A's format to **Text** before entering codes such as `1.10`.

| Product Code | Product Name |
|---|---|
| 1.11 | Product 11 |
| 2.3 | Product 23 |

## Usage

1. Open the scanned PDF.
2. Load the Excel product database.
3. Choose an output folder.
4. Configure items' numbers and names (using the excel form)
4. For each page, search for products, enter quantities, set month/year, then select **Save & Continue**.
5. The resulting filename looks like `1.11x1, 2.3x2, Oct.2026.pdf`.

Existing output files are not silently overwritten. If you rename a previously exported page, the old export is retained and you are notified. The original scanned PDF is never modified.


## Upgrade Priority

> TODO: Update when more functions needed.

| Priority | Feature | Files to modify | Status |
|---|---|---|---|
| 1 | Remember previous selected date | `main_window.py`: `save_and_continue()` | <b>Done</b> |
| 2 | Modify filename in UI |  | <b>In progress</b> |
| 3 | Import expected item quantity | `excel_handler.py`, `excel_config_dialog.py` | <b>Not started</b> |
| 4 | Show quatity warning to user | 	New `quantity_validator.py`, `main_window.py`, tests\ | <b>Not started</b> |
| 5 | Delete wrong files (add review mode, overwrite filenames saved) |  | <b>Not started</b> |


## Excel  comfiguration mapping

Click **Configure product Excel** and choose an `.xlsx` workbook. In the configuration dialog:

1. Select the worksheet from the dropdown.
2. Enter ranges (e.g. `A7:A46` and `B7:B46`) **or** select contiguous vertical cells in the worksheet grid and click the corresponding **Use selected cells** button.
3. Click **Validate ranges and preview mapping**. Check item codes and descriptions.
4. Click **Use this mapping** to return to the PDF organizer.

<!-- Ranges can start on different rows but must have the same number of cells; entries are paired by position. Blank WBS/description pairs are skipped. Missing descriptions and duplicate codes are rejected. The visual worksheet preview is limited to the first 250 rows and 24 columns for performance; you can type any valid range manually.

**Item codes:** Store them as text in Excel for maximum reliability. Numeric cells formatted `0.00` are interpreted using that formatting (e.g. `4.10`). If Excel already lost a trailing zero and no number format retains it, the original code cannot be recovered automatically.

**Testing:** From the project folder, run `python -m unittest discover -s tests -v` (using your virtual environment's Python). The visual dialog must also be tested on Windows. -->
