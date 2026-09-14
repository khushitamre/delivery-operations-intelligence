from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent
RAW = ROOT / 'data' / 'raw'
PROCESSED = ROOT / 'data' / 'processed'
DB = ROOT / 'data' / 'delivery_ops.db'


def load_csv(name):
    return pd.read_csv(RAW / name)


def build():
    PROCESSED.mkdir(parents=True, exist_ok=True)
    orders = load_csv('olist_orders_dataset.csv')
    items = load_csv('olist_order_items_dataset.csv')
    reviews = load_csv('olist_order_reviews_dataset.csv')
    customers = load_csv('olist_customers_dataset.csv')
    sellers = load_csv('olist_sellers_dataset.csv')
    trans = load_csv('product_category_name_translation.csv')
    products = load_csv('olist_products_dataset.csv')[['product_id', 'product_category_name']]

    date_cols = [c for c in orders.columns if c.startswith('order_') and ('date' in c or 'timestamp' in c)]
    for c in date_cols:
        orders[c] = pd.to_datetime(orders[c], errors='coerce')

    items['shipping_limit_date'] = pd.to_datetime(items['shipping_limit_date'], errors='coerce')
    items = items.merge(products, on='product_id', how='left').merge(trans, on='product_category_name', how='left')
    items['product_category_name_english'] = items['product_category_name_english'].fillna('Other')
    item_agg = items.groupby('order_id', as_index=False).agg(
        item_count=('order_item_id','count'), product_value=('price','sum'), freight_value=('freight_value','sum'),
        seller_count=('seller_id','nunique'), seller_id=('seller_id','first'), avg_item_price=('price','mean'),
        category=('product_category_name_english','first'), ship_limit_date=('shipping_limit_date','min')
    )

    reviews = reviews.sort_values('review_creation_date').drop_duplicates('order_id', keep='first')
    reviews = reviews[['order_id','review_score','review_comment_message']]
    customers = customers[['customer_id','customer_unique_id','customer_city','customer_state']]
    sellers = sellers[['seller_id','seller_city','seller_state']]

    fact = orders.merge(customers, on='customer_id', how='left').merge(item_agg, on='order_id', how='left').merge(reviews, on='order_id', how='left').merge(sellers, on='seller_id', how='left')
    fact['order_status'] = fact['order_status'].fillna('unknown')
    fact['category'] = fact['category'].fillna('Other')
    fact['review_score'] = fact['review_score'].fillna(0)
    fact['order_value'] = fact['product_value'].fillna(0) + fact['freight_value'].fillna(0)
    fact['delivery_days'] = (fact['order_delivered_customer_date'] - fact['order_purchase_timestamp']).dt.total_seconds() / 86400
    fact['promised_days'] = (fact['order_estimated_delivery_date'] - fact['order_purchase_timestamp']).dt.total_seconds() / 86400
    fact['late_days'] = (fact['order_delivered_customer_date'] - fact['order_estimated_delivery_date']).dt.total_seconds() / 86400
    fact['late_days'] = fact['late_days'].clip(lower=0)
    fact['is_delivered'] = fact['order_status'].eq('delivered')
    fact['is_late'] = (fact['late_days'] > 0) & fact['is_delivered']
    fact['is_cancelled'] = fact['order_status'].eq('canceled')
    fact['purchase_date'] = fact['order_purchase_timestamp'].dt.date.astype('string')
    fact['purchase_month'] = fact['order_purchase_timestamp'].dt.to_period('M').astype('string')
    fact['purchase_day'] = fact['order_purchase_timestamp'].dt.day_name()
    fact['purchase_hour'] = fact['order_purchase_timestamp'].dt.hour
    fact['weekend_flag'] = fact['order_purchase_timestamp'].dt.dayofweek >= 5
    fact['review_label'] = np.select([fact['review_score'].between(1,2), fact['review_score'].eq(3), fact['review_score'].between(4,5)], ['At risk','Neutral','Healthy'], default='No review')
    fact['delivery_status'] = np.select([fact['is_cancelled'], fact['is_late'], fact['is_delivered']], ['Cancelled','Late','On time'], default='In flight / other')
    fact['distance_proxy'] = np.where(fact['seller_state'].notna() & fact['customer_state'].notna(), (fact['seller_state'] != fact['customer_state']).astype(int), np.nan)

    fact.to_csv(PROCESSED / 'order_fact.csv', index=False)
    with sqlite3.connect(DB) as con:
        fact.to_sql('order_fact', con, if_exists='replace', index=False)
        item_agg.to_sql('order_items_agg', con, if_exists='replace', index=False)
        orders.to_sql('orders_clean', con, if_exists='replace', index=False)
    print(f'Built {len(fact):,} order records at {DB}')

if __name__ == '__main__':
    build()
