# PDF Organizer V1 — Modular Python Desktop Application

One scanned PDF page becomes one output PDF, named from an Excel product database.

## Project layout

```text
PDF_Organizer_V1_Modular/
├── main.py                    # Application entry point only
├── modules/
│   ├── excel_handler.py       # Read Excel product database
│   ├── pdf_handler.py         # Open, preview, export PDF pages
│   ├── filename_generator.py  # Filename rules and date formatting
│   ├── validators.py          # Filename-safe product codes
│   └── page_state.py          # Per-page selections and saved path
├── ui/
│   └── main_window.py         # PySide6 widgets and interactions
├── tests/
│   └── test_core.py           # Filename and Excel tests
├── data/                      # Put your Excel file here (optional)
├── output/                    # Optional export folder
├── requirements.txt
└── build_windows.bat          # Build a Windows executable
```

## No Python installed on the company laptop?

You can **run a prebuilt Windows executable without installing Python**. However, the ZIP contains **source code, not a compiled EXE**. Build the EXE on a separate Windows computer where Python is allowed, or ask your company's IT department to build and approve it. PyInstaller embeds the Python runtime and dependencies.

### Build on an approved Windows computer

1. Install Python 3.11 or 3.12 and extract this ZIP.
2. Open a terminal in the extracted project folder.
3. Run `build_windows.bat` (requires internet for initial dependency installation).
4. Find `dist\PDFOrganizer.exe`.
5. Obtain company IT/security approval before transferring or running it on your work laptop.

Windows executables should be built on Windows. PyInstaller is not a cross-compiler. Company security policies may block unsigned EXEs; do not bypass them.

### Run source code (on a computer with Python)

```powershell
py -m pip install -r requirements.txt
py main.py
```

### Run tests

```powershell
py -m unittest discover -s tests -v
```

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
4. For each page, search for products, enter quantities, set month/year, then select **Save & Continue**.
5. The resulting filename looks like `1.11x1, 2.3x2, Oct 2026.pdf`.

Existing output files are not silently overwritten. If you rename a previously exported page, the old export is retained and you are notified. The original scanned PDF is never modified.

## Limitations

- One scanned page per output PDF; no OCR in V1.
- Product/date selection is manual.
- No automatic session recovery after closing the app.
- Same filename for different pages is rejected; choose distinct naming data.
