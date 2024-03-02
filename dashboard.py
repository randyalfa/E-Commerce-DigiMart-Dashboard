import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import warnings
from babel.numbers import format_currency
from plotly.subplots import make_subplots
warnings.filterwarnings('ignore')
sns.set(style='dark')
st.set_page_config(page_title="DigiMart", page_icon="🛒", layout="wide")

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Helper function yang dibutuhkan untuk menyiapkan berbagai dataframe <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# Fungsi Create Orders by Payment Type
def create_orders_by_payment_type_df(df):
    bypaymenttype_df = df.groupby(by="payment_type").order_id.nunique().reset_index()
    bypaymenttype_df.rename(columns={
        "order_id": "order_count"
    }, inplace=True)
    bypaymenttype_df['payment_type'] = pd.Categorical(bypaymenttype_df['payment_type'], ["boleto", "credit_card", "debit_card", "voucher"])

    return bypaymenttype_df

# Fungsi Create Orders Income per Month 2017
def create_orders_income_per_month_2017_df(df):
    monthly_orders_2017_df = df.resample(rule='M', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    }).reset_index()

    monthly_orders_2017_df = monthly_orders_2017_df[monthly_orders_2017_df['order_purchase_timestamp'].apply(lambda x: str(x.year).startswith('2017'))]
    monthly_orders_2017_df['order_purchase_timestamp'] = pd.to_datetime(monthly_orders_2017_df['order_purchase_timestamp']).dt.strftime('%B')
    monthly_orders_2017_df.rename(columns={
        "order_purchase_timestamp": "order_date",
        "order_id": "total_orders",
        "payment_value": "income"
    }, inplace=True)

    return monthly_orders_2017_df

# Fungsi Create Orders Income per Month 2018
def create_orders_income_per_month_2018_df(df):
    monthly_orders_2018_df = df.resample(rule='M', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    }).reset_index()

    monthly_orders_2018_df = monthly_orders_2018_df[monthly_orders_2018_df['order_purchase_timestamp'].apply(lambda x: str(x.year).startswith('2018'))]
    monthly_orders_2018_df['order_purchase_timestamp'] = pd.to_datetime(monthly_orders_2018_df['order_purchase_timestamp']).dt.strftime('%B')
    monthly_orders_2018_df.rename(columns={
        "order_purchase_timestamp": "order_date",
        "order_id": "total_orders",
        "payment_value": "income"
    }, inplace=True)

    return monthly_orders_2018_df

# Fungsi Create Orders by Delivery Time <= 10 hari
def create_orders_by_delivery_time_10_df(df):
    filtered_delivery_time_df = df[df['delivery_time'] < 11.0]

    delivery_time_10d_df = filtered_delivery_time_df.groupby(by="delivery_time").order_id.nunique().reset_index()
    delivery_time_10d_df.rename(columns={
        "order_id": "order_count"
    }, inplace=True)

    return delivery_time_10d_df

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Load cleaned data <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< 
all_df = pd.read_csv("https://raw.githubusercontent.com/randyalfa/E-Commerce-All-Orders-Dataset/master/all_orders_data.csv")

datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Filter data <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://raw.githubusercontent.com/randyalfa/E-Commerce-Public-Dataset/master/DigiMart.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Time Interval',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Menyiapkan berbagai dataframe <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< 
orders_by_payment_type_df = create_orders_by_payment_type_df(main_df)
orders_income_per_month_2017_df = create_orders_income_per_month_2017_df(main_df)
orders_income_per_month_2018_df = create_orders_income_per_month_2018_df(main_df)
orders_by_delivery_time_10_df = create_orders_by_delivery_time_10_df(main_df)

# Header
st.header('🛒 E-Commerce DigiMart Orders Summary')

col1, col2, col3 = st.columns(3)
with col1:
    total_orders = main_df.order_id.count()
    st.metric("Total Orders", value=total_orders)

with col2:
    total_transactions = format_currency(main_df.payment_value.sum(), "US $", locale='es_US') 
    st.metric("Total Transactions", value=total_transactions)

with col3:
    average_transactions = format_currency(main_df.payment_value.mean(), 'US $', locale='en_US')
    st.metric("Average Transactions", value=average_transactions)

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Number of Orders by Payment Type <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< 
st.subheader('Number of Orders by Payment Type')
 
fig = px.bar(
    orders_by_payment_type_df.sort_values(by="payment_type", ascending=False),
    x="payment_type",
    y="order_count",
    color_discrete_sequence=["#EE4035"],
    labels={"order_count": "Number of Orders", "payment_type": "Payment Type"}
)

st.plotly_chart(fig)

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Number of Orders and Total Income per Month in 2017/2018 <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< 
st.subheader('Number of Orders & Total Income per Month in 2017/2018')

dataframes = [orders_income_per_month_2017_df, orders_income_per_month_2018_df]

def create_line_plot(df, year):
    if df is not None and year is not None:
        fig = make_subplots(rows=1, cols=2, subplot_titles=((f"Number of Orders per Month in {year}"), (f"Total Income per Month in {year}")))

        fig.add_trace(
            go.Scatter(x=df['order_date'], y=df['total_orders'], mode='lines', name='Total Orders', line=dict(color='#F37736')),
            row=1, col=1
        )
        fig.update_xaxes(title_text=None, tickangle=45)
        fig.update_xaxes(title_text=None)
        fig.update_yaxes(title_text=None)

        fig.add_trace(
            go.Scatter(x=df['order_date'], y=df['income'], mode='lines', name='Income', line=dict(color='#FDF498')),
            row=1, col=2
        )
        fig.update_xaxes(title_text=None, tickangle=45)
        fig.update_xaxes(title_text=None)
        fig.update_yaxes(title_text=None)

        fig.update_layout(width=1420, showlegend=False, title=f'Number of Orders and Total Income per Month in {year}')
        return fig

years_available = []

if str(start_date).startswith('2017') and str(end_date).startswith('2017'):
    years_available.extend(['2017'])
if str(start_date).startswith('2018') and str(end_date).startswith('2018'):
    years_available.extend(['2018'])
if str(start_date).startswith('2017') and str(end_date).startswith('2018'):
    years_available.extend(['2017', '2018'])
else:
    years_available.extend(['2017', '2018'])

# Tampilkan dropdown untuk memilih tahun
selected_year = st.selectbox('Select Year', years_available)

# Ambil DataFrame berdasarkan indeks yang sesuai dengan tahun yang dipilih
selected_df = dataframes[int(selected_year) - 2017]

# Buat plot line berdasarkan DataFrame yang dipilih
fig = create_line_plot(selected_df, selected_year)

# Tampilkan plot menggunakan plotly_chart
st.plotly_chart(fig)

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Number of Orders with Delivery Time Less Than 10 Day <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
st.subheader('Number of Orders with Delivery Time Less Than 10 Day')

fig = px.bar(
    orders_by_delivery_time_10_df.sort_values(by="delivery_time", ascending=False),
    y="order_count",
    x="delivery_time",
    labels={"order_count": "Number of Orders", "delivery_time": "Day"},
    color_discrete_sequence=["#0392CF"]
)

fig.update_layout(
    xaxis=dict(tickmode='linear', tickfont=dict(size=12)),
    yaxis_title="Number of Orders",
    xaxis_title="Day",
)

st.plotly_chart(fig)

st.caption('Copyright © Muhammad Haswan Alfarandy 2024')