from pathlib import Path
from urllib.request import urlretrieve

ROOT = Path(__file__).resolve().parent
RAW = ROOT / 'data' / 'raw'
RAW.mkdir(parents=True, exist_ok=True)
BASE = 'https://raw.githubusercontent.com/olist/work-at-olist-data/master/datasets/'
FILES = [
    'olist_orders_dataset.csv',
    'olist_order_items_dataset.csv',
    'olist_order_reviews_dataset.csv',
    'olist_customers_dataset.csv',
    'olist_sellers_dataset.csv',
    'olist_products_dataset.csv',
    'product_category_name_translation.csv',
]

for name in FILES:
    target = RAW / name
    if target.exists() and target.stat().st_size > 0:
        print(f'Skipping existing file: {name}')
        continue
    print(f'Downloading: {name}')
    urlretrieve(BASE + name, target)

print(f'Dataset files are ready in {RAW}')
