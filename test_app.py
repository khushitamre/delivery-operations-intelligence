from pathlib import Path
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent

for page in ['Executive Overview', 'Delivery Performance', 'Customer Experience', 'Seller & Zone Operations', 'Decision Lab']:
    at = AppTest.from_file(str(ROOT / 'app.py')).run(timeout=30)
    if at.exception:
        raise at.exception[0].value
    at.radio[0].set_value(page).run(timeout=30)
    if at.exception:
        raise at.exception[0].value
    print(f'PASS: {page}')
