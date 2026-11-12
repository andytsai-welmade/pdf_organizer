import re

INVALID_FILENAME = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


# Check the validity of custom filename 
def validate_custom_filename(filename: str) -> str:
    filename = filename.strip()

    if not filename:
        raise ValueError("Filename cannot be empty.")

    if INVALID_FILENAME.search(filename):
        raise ValueError("Filename contains invalid characters.")

    if not filename.lower().endswith(".pdf"):
        raise ValueError("Filename must end with .pdf.")

    stem = filename[:-4]

    if not stem or stem.endswith((".", " ")):
        raise ValueError("Invalid filename.")

    if stem.upper().split(".")[0] in {
        "CON", "PRN", "AUX", "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }:
        raise ValueError("Reserved Windows filename.")

    return filename

