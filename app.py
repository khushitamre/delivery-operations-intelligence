from pathlib import Path
import sqlite3
import subprocess
import sys
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parent
DB = ROOT / 'data' / 'delivery_ops.db'

st.set_page_config(page_title='Delivery Operations Intelligence', page_icon='▦', layout='wide', initial_sidebar_state='expanded')

st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
h1,h2,h3 { font-family:'Space Grotesk',sans-serif; letter-spacing:-.02em; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1450px; }
[data-testid="stSidebar"] { background: #111827; }
[data-testid="stSidebar"] * { color: #e5e7eb !important; }
.hero { background: linear-gradient(115deg,#0f172a,#1e293b 70%,#164e63); color:white; padding:28px 34px; border-radius:18px; margin-bottom:22px; }
.eyebrow { color:#67e8f9; font-size:12px; font-weight:700; letter-spacing:.14em; text-transform:uppercase; }
.hero h1 { font-size:34px; margin:8px 0 4px; }
.hero p { color:#cbd5e1; margin:0; font-size:15px; }
.kpi { border:1px solid #e2e8f0; border-radius:14px; padding:16px 18px; background:#fff; box-shadow:0 3px 14px rgba(15,23,42,.04); }
.kpi-label { color:#64748b; font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:.06em; }
.kpi-value { color:#0f172a; font-size:26px; font-weight:700; margin-top:7px; }
.kpi-note { color:#64748b; font-size:12px; margin-top:3px; }
.insight { border-left:4px solid #0891b2; background:#ecfeff; padding:12px 15px; border-radius:0 10px 10px 0; color:#164e63; margin:8px 0; }
.small {color:#64748b;font-size:12px}
.top-nav [data-testid="stRadio"] > div { gap: 8px; }
.top-nav label { background:#e2e8f0; border-radius:999px; padding:8px 16px; color:#334155 !important; font-weight:600; }
.top-nav label:has(input:checked) { background:#0f172a; color:#ffffff !important; }
</style>''', unsafe_allow_html=True)

@st.cache_data
def load_data():
    with sqlite3.connect(DB) as con:
        df = pd.read_sql('select * from order_fact', con, parse_dates=['order_purchase_timestamp','order_delivered_customer_date','order_estimated_delivery_date','order_approved_at','order_delivered_carrier_date','order_delivered_customer_date'])
    return df

# fix indentation-safe function definition workaround
load_data = load_data

def ensure_data_mart():
    """Bootstrap ignored public data files on Streamlit Cloud's first run."""
    if DB.exists():
        return True
    with st.status('Preparing the public Olist data mart (first run only)...', expanded=True) as status:
        try:
            st.write('Downloading public source files...')
            subprocess.run([sys.executable, str(ROOT / 'download_data.py')], check=True, capture_output=True, text=True)
            st.write('Building the SQLite analytical data mart...')
            result = subprocess.run([sys.executable, str(ROOT / 'prepare_data.py')], check=True, capture_output=True, text=True)
            st.write(result.stdout.strip())
            status.update(label='Data mart ready. Loading dashboard...', state='complete', expanded=False)
            return True
        except subprocess.CalledProcessError as exc:
            status.update(label='Data preparation failed', state='error', expanded=True)
            st.error(exc.stderr or str(exc))
            return False

if not ensure_data_mart():
    st.stop()
df = load_data()

with st.sidebar:
    st.markdown('## Filters')
    st.caption('Scope the operating view')
    st.divider()
    states = st.multiselect('Customer state', sorted(df['customer_state'].dropna().unique()), default=[])
    statuses = st.multiselect('Order status', sorted(df['order_status'].dropna().unique()), default=[])
    date_min, date_max = df['order_purchase_timestamp'].min().date(), df['order_purchase_timestamp'].max().date()
    date_range = st.date_input('Purchase date range', (date_min, date_max), min_value=date_min, max_value=date_max)
    st.divider()
    st.caption('Independent analytical prototype')
    st.caption('Source: Olist Brazilian E-Commerce Public Dataset')

f = df.copy()
if states: f = f[f.customer_state.isin(states)]
if statuses: f = f[f.order_status.isin(statuses)]
if isinstance(date_range, tuple) and len(date_range)==2: f = f[f.order_purchase_timestamp.dt.date.between(date_range[0], date_range[1])]

st.markdown('<div class="hero"><div class="eyebrow">Operations command center · 2016—2018 public benchmark</div><h1>Delivery Operations Intelligence</h1><p>Diagnose late delivery, cancellation and customer-experience leakage before it becomes an operations problem.</p></div>', unsafe_allow_html=True)

st.markdown('<div class="top-nav">', unsafe_allow_html=True)
page = st.radio('Workspace', ['Executive Overview','Delivery Performance','Customer Experience','Seller & Zone Operations','Decision Lab'], horizontal=True, label_visibility='collapsed')
st.markdown('</div>', unsafe_allow_html=True)
st.divider()

def money(x): return f'R$ {x:,.0f}'
def pct(x): return f'{x:.1%}'
def kpi(label, value, note): st.markdown(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-note">{note}</div></div>', unsafe_allow_html=True)
def chart(fig, height=360):
    fig.update_layout(template='plotly_white', height=height, margin=dict(l=10,r=10,t=45,b=10), font=dict(family='DM Sans'), legend=dict(orientation='h', y=1.08))
    st.plotly_chart(fig, width='stretch', config={'displayModeBar':False})

if page == 'Executive Overview':
    delivered = f[f['is_delivered'].astype(bool)]
    late_rate = delivered.is_late.mean() if len(delivered) else 0
    cancel_rate = f.is_cancelled.mean() if len(f) else 0
    rating = f.loc[f.review_score>0,'review_score'].mean() if (f.review_score>0).any() else 0
    est_leak = f.loc[f['is_late'].astype(bool),'order_value'].sum()*0.12 + f.loc[f['is_cancelled'].astype(bool),'order_value'].sum()
    cols = st.columns(5)
    for c,(a,b,d) in zip(cols,[('Orders',f'{len(f):,}','Filtered order volume'),('On-time rate',pct(1-late_rate),'Delivered orders only'),('Cancellation rate',pct(cancel_rate),'Order-level'),('Avg rating',f'{rating:.2f}/5','Reviewed orders'),('At-risk value',money(est_leak),'Directional exposure estimate')]):
        with c: kpi(a,b,d)
    st.markdown('### Operating signal')
    c1,c2=st.columns([1.35,1])
    with c1:
        monthly=f.groupby('purchase_month',as_index=False).agg(orders=('order_id','count'),late_rate=('is_late','mean'),cancel_rate=('is_cancelled','mean'))
        fig=go.Figure(); fig.add_trace(go.Scatter(x=monthly.purchase_month,y=monthly.late_rate*100,name='Late rate %',mode='lines+markers',line=dict(color='#0891b2',width=3))); fig.add_trace(go.Scatter(x=monthly.purchase_month,y=monthly.cancel_rate*100,name='Cancellation %',mode='lines+markers',line=dict(color='#f97316',width=3))); fig.update_yaxes(title='Rate (%)'); fig.update_layout(title='Service-risk trend'); chart(fig,350)
    with c2:
        state=f.groupby('customer_state',as_index=False).agg(orders=('order_id','count'),late_rate=('is_late','mean'),avg_rating=('review_score','mean')).query('orders >= 100').sort_values('late_rate',ascending=False).head(10)
        chart(px.bar(state,y='customer_state',x='late_rate',orientation='h',color='late_rate',color_continuous_scale='Teal',title='Highest late-rate markets (min. 100 orders)').update_xaxes(tickformat='.1%'),350)
    st.markdown('### Management readout')
    topcat=f.groupby('category',as_index=False).agg(orders=('order_id','count'),late_rate=('is_late','mean'),rating=('review_score','mean')).query('orders >= 100').sort_values('late_rate',ascending=False).head(5)
    insights=[f"Service risk is {late_rate:.1%} across delivered orders; prioritize the top markets and categories rather than applying a blanket intervention.",f"The current directional exposure estimate is {money(est_leak)}; it combines cancelled order value with a conservative late-order experience provision and is not reported financial loss.",f"{topcat.iloc[0]['category']} is the highest late-rate category among scaled categories at {topcat.iloc[0]['late_rate']:.1%}. Validate seller mix and fulfillment handling before changing customer promises."] if len(topcat) else ['Apply broader filters to generate an operating readout.']
    for x in insights: st.markdown(f'<div class="insight">{x}</div>',unsafe_allow_html=True)

elif page == 'Delivery Performance':
    st.subheader('Delivery Performance')
    st.caption('A root-cause view of the customer promise: elapsed delivery time, promise variance and service risk.')
    delivered=f[f['is_delivered'].astype(bool) & f.delivery_days.notna()]
    c1,c2,c3=st.columns(3)
    with c1:kpi('Median delivery time',f"{delivered.delivery_days.median():.1f} days",'Purchase to customer delivery')
    with c2:kpi('Late-order variance',f"{delivered.loc[delivered.is_late,'late_days'].mean():.1f} days",'Average days beyond estimate')
    with c3:kpi('90th percentile',f"{delivered.delivery_days.quantile(.9):.1f} days",'Long-tail customer experience')
    byday=delivered.groupby('purchase_day',as_index=False).agg(orders=('order_id','count'),avg_days=('delivery_days','mean'),late_rate=('is_late','mean')).sort_values('late_rate',ascending=False)
    c1,c2=st.columns(2)
    with c1: chart(px.bar(byday,x='purchase_day',y='late_rate',color='late_rate',color_continuous_scale='Teal',title='Late rate by purchase day').update_yaxes(tickformat='.1%'))
    with c2: chart(px.scatter(byday,x='avg_days',y='late_rate',size='orders',text='purchase_day',title='Speed vs reliability by purchase day').update_yaxes(tickformat='.1%'))
    cat=delivered.groupby('category',as_index=False).agg(orders=('order_id','count'),delivery_days=('delivery_days','median'),late_rate=('is_late','mean'),rating=('review_score','mean')).query('orders >= 100').sort_values('late_rate',ascending=False).head(20)
    chart(px.bar(cat.sort_values('late_rate'),x='late_rate',y='category',orientation='h',color='rating',title='Category risk matrix — scaled categories',color_continuous_scale='RdYlGn').update_xaxes(tickformat='.1%'))
    st.dataframe(cat.style.format({'delivery_days':'{:.1f}','late_rate':'{:.1%}','rating':'{:.2f}'}),width='stretch',hide_index=True)

elif page == 'Customer Experience':
    st.subheader('Customer Experience')
    st.caption('Connect service failure to review outcomes and protect the moments that matter.')
    review=f[f.review_score>0].copy(); review['late_group']=np.where(review['is_late'].astype(bool),'Late','On time / other')
    c1,c2=st.columns(2)
    with c1: chart(px.box(review,x='late_group',y='review_score',color='late_group',title='Customer rating distribution by delivery outcome',color_discrete_map={'Late':'#f97316','On time / other':'#0891b2'}))
    with c2:
        rr=review.groupby('review_label',as_index=False).size().rename(columns={'size':'orders'}); chart(px.pie(rr,names='review_label',values='orders',hole=.55,title='Review health mix',color='review_label',color_discrete_map={'Healthy':'#0891b2','Neutral':'#f59e0b','At risk':'#ef4444'}))
    heat=review.groupby(['purchase_day','review_label'],as_index=False).size().rename(columns={'size':'orders'})
    chart(px.density_heatmap(review,x='purchase_hour',y='review_score',nbinsx=24,title='Experience pattern by purchase hour',color_continuous_scale='Teal'))
    st.markdown('### Experience intervention queue')
    queue=f.groupby('category',as_index=False).agg(orders=('order_id','count'),late_rate=('is_late','mean'),rating=('review_score','mean'),at_risk=('review_label',lambda x:(x=='At risk').sum())).query('orders >= 100').sort_values(['at_risk','late_rate'],ascending=False).head(15)
    st.dataframe(queue.style.format({'late_rate':'{:.1%}','rating':'{:.2f}'}),width='stretch',hide_index=True)

elif page == 'Seller & Zone Operations':
    st.subheader('Seller & Zone Operations')
    st.caption('Prioritize the operational nodes where a targeted intervention can move service metrics.')
    seller=f.groupby(['seller_id','seller_state'],as_index=False).agg(orders=('order_id','count'),late_rate=('is_late','mean'),avg_days=('delivery_days','mean'),rating=('review_score','mean'),order_value=('order_value','sum')).query('orders >= 30').sort_values('late_rate',ascending=False)
    c1,c2=st.columns(2)
    with c1: chart(px.scatter(seller,x='orders',y='late_rate',size='order_value',color='rating',hover_data=['seller_id','seller_state'],title='Seller risk / scale map',color_continuous_scale='RdYlGn').update_yaxes(tickformat='.1%'))
    with c2:
        zone=f.groupby('customer_state',as_index=False).agg(orders=('order_id','count'),late_rate=('is_late','mean'),cancel_rate=('is_cancelled','mean'),rating=('review_score','mean')).query('orders >= 100').sort_values('orders',ascending=False).head(20)
        chart(px.bar(zone.sort_values('late_rate'),x='late_rate',y='customer_state',orientation='h',color='cancel_rate',title='Market service profile',color_continuous_scale='Oranges').update_xaxes(tickformat='.1%'))
    st.markdown('### Seller intervention queue')
    seller['priority_score']=(seller.late_rate*100 + (5-seller.rating.fillna(3))*8)*np.log1p(seller.orders)
    out=seller.sort_values('priority_score',ascending=False).head(25)
    st.dataframe(out[['seller_id','seller_state','orders','late_rate','avg_days','rating','order_value','priority_score']].style.format({'late_rate':'{:.1%}','avg_days':'{:.1f}','rating':'{:.2f}','order_value':'R$ {:,.0f}','priority_score':'{:.1f}'}),width='stretch',hide_index=True)

else:
    st.subheader('Decision Lab')
    st.caption('Translate operational assumptions into a defensible prioritization view. This is a scenario tool, not a causal forecast.')
    c1,c2,c3=st.columns(3)
    with c1: late_reduction=st.slider('Target late-rate reduction',0.05,0.50,0.20,0.05)
    with c2: save_per_late=st.number_input('Experience provision per late order (R$)',0,500,35,5)
    with c3: intervention_cost=st.number_input('Intervention cost (R$)',0,100000,15000,1000)
    late_orders=int(f.is_late.sum()); avoided=late_orders*late_reduction; benefit=avoided*save_per_late; roi=(benefit-intervention_cost)/intervention_cost if intervention_cost else np.nan
    cols=st.columns(4)
    for c,(a,b,d) in zip(cols,[('Current late orders',f'{late_orders:,}','Filtered scope'),('Avoided late orders',f'{avoided:,.0f}',f'At {late_reduction:.0%} improvement'),('Directional benefit',money(benefit),'Scenario estimate'),('Scenario ROI',f'{roi:.1%}','Benefit less cost / cost')]):
        with c:kpi(a,b,d)
    st.markdown('### Recommended operating playbook')
    st.markdown('<div class="insight"><b>1 · Diagnose:</b> Start with sellers and customer states in the intervention queue, using a minimum-volume threshold to avoid noisy decisions.</div><div class="insight"><b>2 · Pilot:</b> Test a narrow intervention such as promise recalibration, seller dispatch SLA review or peak-hour capacity balancing.</div><div class="insight"><b>3 · Measure:</b> Compare late rate, cancellation rate and review score against a matched baseline. Do not treat correlation as proof of causality.</div>',unsafe_allow_html=True)
    st.download_button('Download filtered order fact',f.to_csv(index=False).encode(),file_name='delivery_ops_filtered_orders.csv',mime='text/csv')

st.divider(); st.caption('Method note: This independent prototype uses the anonymized Olist Brazilian E-Commerce Public Dataset. It is not an internal analysis of any delivery company. “At-risk value” and ROI outputs are directional scenarios requiring operational validation.')
