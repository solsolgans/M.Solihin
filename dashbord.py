import streamlit as st
import pandas as pd
import plotly.express as px

# Inisialisasi session state untuk tema jika belum ada
if 'theme' not in st.session_state:
    st.session_state['theme'] = 'light'

# Fungsi untuk mengubah tema
def toggle_theme():
    if st.session_state['theme'] == 'light':
        st.session_state['theme'] = 'dark'
    else:
        st.session_state['theme'] = 'light'

# Load dataset dari Google Drive
@st.cache_data
def load_data():
    order_df = pd.read_csv("https://drive.google.com/uc?id=1xF5BlF2gKryr0UiJ4T1dyZk0Naf-irob", parse_dates=['order_purchase_timestamp', 'order_delivered_customer_date', 'order_estimated_delivery_date'])
    order_item_df = pd.read_csv("https://drive.google.com/uc?id=1bbiSGtezbR97_SXRg6r201u4IPM37-Yc")
    products_df = pd.read_csv("https://drive.google.com/uc?id=1hsDHePmIcWb2qlyOIftgZQh-3UJCQbSy")
    customer_df = pd.read_csv("https://drive.google.com/uc?id=1JMWkiBoyfCOPGi5Th1CxMA2D7PCsvf8K")
    order_review_df = pd.read_csv("https://drive.google.com/uc?id=1sqmrpSC55RDMG1rSwmQOoxM0nt4uEYKY")
    return order_df, order_item_df, products_df, customer_df, order_review_df

# Load data
order_df, order_item_df, products_df, customer_df, order_review_df = load_data()

# Atur tema berdasarkan session state
theme = st.session_state['theme']
if theme == 'dark':
    bg_color = "#1E1E1E"
    text_color = "#FFFFFF"
    sidebar_bg = "#2E2E2E"
    button_label = "🌞 Terang"
else:
    bg_color = "#FFFFFF"
    text_color = "#000000"
    sidebar_bg = "#F0F2F6"
    button_label = "🌙 Gelap"

# Terapkan CSS untuk tema
st.markdown(f"""
    <style>
        body {{ background-color: {bg_color}; color: {text_color}; }}
        .stApp {{ background-color: {bg_color}; color: {text_color}; }}
        .sidebar .sidebar-content {{ background-color: {sidebar_bg}; }}
        .stTextInput, .stSelectbox, .stMultiselect, .stButton {{ color: {text_color}; }}
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigasi
st.sidebar.title("MENU💰")
st.sidebar.button(button_label, on_click=toggle_theme)

# Filter berdasarkan kategori produk
all_categories = products_df['product_category_name'].dropna().unique()
selected_categories = st.sidebar.multiselect("Pilih kategori produk untuk melihat produk terlaris dan tren jumlah pesanan:", all_categories, default=all_categories[:5])

# Filter data berdasarkan kategori
filtered_orders = order_item_df.merge(products_df, on='product_id', how='left')
filtered_orders = filtered_orders[filtered_orders['product_category_name'].isin(selected_categories)]
filtered_orders = filtered_orders.merge(order_df[['order_id', 'order_purchase_timestamp']], on='order_id', how='left')

st.sidebar.markdown("---")
st.sidebar.write("Dibuat oleh **Muhammad Solihin**")
st.title("📊 Dashboard E-Commerce")

# Produk Terlaris
top_products = filtered_orders.groupby("product_category_name").size().reset_index(name='total_orders')
top_products = top_products.nlargest(10, 'total_orders')
fig = px.bar(top_products, x='product_category_name', y='total_orders', title='📊 Produk Terlaris')
st.plotly_chart(fig)

# Jumlah Pesanan
filtered_orders['year_month'] = filtered_orders['order_purchase_timestamp'].dt.strftime('%Y-%m')
order_trend = filtered_orders.groupby('year_month').size().reset_index(name='total_orders')
fig = px.line(order_trend, x='year_month', y='total_orders', title='📈 Tren Jumlah Pesanan')
fig.update_xaxes(type='category')
st.plotly_chart(fig)

# Kota dengan Jumlah Pembelian Terbanyak
top_cities = customer_df['customer_city'].value_counts().head(10)
fig = px.bar(x=top_cities.index, y=top_cities.values, title='🏙️ Kota dengan Jumlah Pembelian Terbanyak')
st.plotly_chart(fig)
st.write("\n**Analisis:** Sao Paulo mendominasi e-commerce, menunjukkan bahwa e-commerce lebih berkembang di kota metropolitan dengan infrastruktur dan daya beli yang lebih tinggi.")

# Hubungan Rating dengan Repeat Order
order_review_df['review_score'] = order_review_df['review_score'].astype(int)
repeat_order = order_review_df.groupby('review_score').size().reset_index(name='avg_repeat_orders')
fig = px.bar(repeat_order, x='review_score', y='avg_repeat_orders', title='⭐ Hubungan Rating dengan Repeat Order')
st.plotly_chart(fig)
st.write("\n**Analisis:** Tidak ada korelasi signifikan antara rating pelanggan dengan repeat orders, menunjukkan faktor lain seperti harga dan kebutuhan lebih berpengaruh.")

# Pengaruh Keterlambatan terhadap Rating
order_df = order_df.dropna(subset=['order_delivered_customer_date'])  # Hindari error NaN
order_df['delay'] = (order_df['order_delivered_customer_date'] - order_df['order_estimated_delivery_date']).dt.days
order_df['is_late'] = order_df['delay'].apply(lambda x: 1 if x > 0 else 0)
avg_rating = order_df.merge(order_review_df, on='order_id').groupby('is_late')['review_score'].mean().reset_index()
fig = px.line(avg_rating, x='is_late', y='review_score', markers=True, title='🚚 Pengaruh Keterlambatan terhadap Rating')
st.plotly_chart(fig)
st.write("\n**Analisis:** Keterlambatan pengiriman terbukti menurunkan rating pelanggan secara signifikan, menunjukkan bahwa ketepatan waktu sangat mempengaruhi kepuasan pelanggan.")
