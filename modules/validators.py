import re

INVALID_FILENAME = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
