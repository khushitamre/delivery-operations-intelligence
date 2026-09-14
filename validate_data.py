from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parent
DB = ROOT / 'data' / 'delivery_ops.db'

REQUIRED = {'order_id','order_status','order_purchase_timestamp','order_value','is_delivered','is_late','is_cancelled','delivery_status','review_score'}

def main():
    assert DB.exists(), f'Missing data mart: {DB}. Run python prepare_data.py first.'
    with sqlite3.connect(DB) as con:
        df = pd.read_sql('select * from order_fact', con)
    assert len(df) >= 90000, f'Unexpectedly small fact table: {len(df)}'
    assert REQUIRED.issubset(df.columns), f'Missing columns: {REQUIRED - set(df.columns)}'
    assert df.order_id.notna().all(), 'order_id contains nulls'
    assert df.order_id.is_unique, 'order grain is not unique'
    assert df.order_value.ge(0).all(), 'order_value contains negative values'
    assert df.review_score.between(0, 5).all(), 'review_score outside 0-5'
    assert df.is_late.isin([0,1,True,False]).all(), 'is_late is not boolean-like'
    delivered = df[df.is_delivered.astype(bool)]
    assert delivered.is_late.astype(bool).le(True).all()
    print(f'PASS: {len(df):,} unique order records; {len(delivered):,} delivered records; {df.order_status.nunique()} statuses.')

if __name__ == '__main__':
    main()
