import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset dari Google Drive
@st.cache_data
def load_data():
    order_df = pd.read_csv("https://drive.google.com/uc?id=1xF5BlF2gKryr0UiJ4T1dyZk0Naf-irob")
    geolocation_df = pd.read_csv("https://drive.google.com/uc?id=1rYMxelhTadgWY47zjoFZN3gslbEOZZj_")
    order_item_df = pd.read_csv("https://drive.google.com/uc?id=1bbiSGtezbR97_SXRg6r201u4IPM37-Yc")
    order_review_df = pd.read_csv("https://drive.google.com/uc?id=1sqmrpSC55RDMG1rSwmQOoxM0nt4uEYKY")
    customer_df = pd.read_csv("https://drive.google.com/uc?id=1JMWkiBoyfCOPGi5Th1CxMA2D7PCsvf8K")
    order_payment_df = pd.read_csv("https://drive.google.com/uc?id=1G3jIWRXmlon5pej5-cktpIuL-vs65g6j")
    products_df = pd.read_csv("https://drive.google.com/uc?id=1hsDHePmIcWb2qlyOIftgZQh-3UJCQbSy")
    seller_df = pd.read_csv("https://drive.google.com/uc?id=1AiJ90xua1lKpGPffAYBXEiaoAFkObd1b")
    product_category_df = pd.read_csv("https://drive.google.com/uc?id=1UOnHFNy4RaPlYxiereMlMfQgnXNVKimE")
    return order_df, geolocation_df, order_item_df, order_review_df, customer_df, order_payment_df, products_df, seller_df, product_category_df

# Load data
order_df, geolocation_df, order_item_df, order_review_df, customer_df, order_payment_df, products_df, seller_df, product_category_df = load_data()

# Sidebar Navigasi
st.sidebar.title("Dashboard E-Commerce")
page = st.sidebar.radio("Pilih Analisis", ["Produk Terlaris", "Jumlah Pesanan", "Kota Terbanyak", "Hubungan Rating & Repeat Order", "Pengaruh Keterlambatan"])

# **1. Produk Terlaris**
if page == "Produk Terlaris":
    st.title("📊 Produk Terlaris")
    top_products = order_item_df.groupby("product_id").size().reset_index(name='total_orders')
    top_products = top_products.merge(products_df, on='product_id')
    top_products = top_products.nlargest(10, 'total_orders')
    fig = px.bar(top_products, x='product_category_name', y='total_orders', title='Top 10 Produk Terlaris')
    st.plotly_chart(fig)
    
    # Kesimpulan
    st.write("\n**Analsis:** Dari visualisasi tersebut, kategori "moveis_decoracao" (furniture dan dekorasi) menjadi produk yang paling laris, diikuti oleh "cama_mesa_banho" (peralatan tempat tidur dan kamar mandi) serta "ferramentas_jardim" (perkakas taman). Hal ini menunjukkan bahwa pelanggan memiliki minat yang tinggi terhadap produk-produk rumah tangga dan dekorasi Kategori seperti "informatica_acessorios" (aksesoris komputer), "relogios_presentes" (jam tangan & hadiah), dan "beleza_saude" (kecantikan & kesehatan) juga cukup diminati, tetapi jumlah pembeliannya lebih sedikit dibandingkan dengan tiga kategori teratas.")

# **2. Tren Jumlah Pesanan**
elif page == "Jumlah Pesanan":
    st.title("📈 Tren Jumlah Pesanan")
    order_df['order_purchase_timestamp'] = pd.to_datetime(order_df['order_purchase_timestamp'])
    order_df['year_month'] = order_df['order_purchase_timestamp'].dt.strftime('%Y-%m')  # Perbaikan disini
    order_trend = order_df.groupby('year_month').size().reset_index(name='total_orders')
    
    fig = px.line(order_trend, x='year_month', y='total_orders', title='Jumlah Pesanan dari Waktu ke Waktu')
    fig.update_xaxes(type='category')  # Pastikan sumbu x bertipe kategori agar tidak ada error
    
    st.plotly_chart(fig)
    
    # Kesimpulan
    st.write("\n**Analisis:** Tren jumlah pesanan meningkat signifikan dari awal 2017 hingga puncaknya di awal 2018, kemungkinan dipengaruhi oleh musim liburan atau promosi.")

# **3. Kota dengan Jumlah Pembelian Terbanyak**
elif page == "Kota Terbanyak":
    st.title("🏙️ Kota dengan Jumlah Pembelian Terbanyak")
    top_cities = customer_df['customer_city'].value_counts().head(10)
    fig = px.bar(x=top_cities.index, y=top_cities.values, title='Top 10 Kota dengan Pembelian Terbanyak')
    st.plotly_chart(fig)
    
    # Kesimpulan
    st.write("\n**Analisis:** Sao Paulo mendominasi e-commerce, menunjukkan bahwa e-commerce lebih berkembang di kota metropolitan dengan infrastruktur dan daya beli yang lebih tinggi.")

# **4. Hubungan Rating dengan Repeat Order**
elif page == "Hubungan Rating & Repeat Order":
    st.title("⭐ Hubungan Rating dengan Repeat Order")
    order_review_df['review_score'] = order_review_df['review_score'].astype(int)
    repeat_order = order_review_df.groupby('review_score').size().reset_index(name='avg_repeat_orders')
    fig = px.bar(repeat_order, x='review_score', y='avg_repeat_orders', title='Hubungan Rating dengan Repeat Orders')
    st.plotly_chart(fig)
    
    # Kesimpulan
    st.write("\n**Analisis:** Tidak ada korelasi signifikan antara rating pelanggan dengan repeat orders, menunjukkan faktor lain seperti harga dan kebutuhan lebih berpengaruh.")

# **5. Pengaruh Keterlambatan terhadap Rating**
elif page == "Pengaruh Keterlambatan":
    st.title("🚚 Pengaruh Keterlambatan terhadap Rating")
    order_df['delay'] = (pd.to_datetime(order_df['order_delivered_customer_date']) - pd.to_datetime(order_df['order_estimated_delivery_date'])).dt.days
    order_df['is_late'] = order_df['delay'].apply(lambda x: 1 if x > 0 else 0)
    avg_rating = order_df.merge(order_review_df, on='order_id').groupby('is_late')['review_score'].mean().reset_index()
    fig = px.line(avg_rating, x='is_late', y='review_score', markers=True, title='Pengaruh Keterlambatan terhadap Rating')
    st.plotly_chart(fig)
    
    # Kesimpulan
    st.write("\n**Analisis:** Keterlambatan pengiriman terbukti menurunkan rating pelanggan secara signifikan, menunjukkan bahwa ketepatan waktu sangat mempengaruhi kepuasan pelanggan.")

st.sidebar.markdown("---")
st.sidebar.write("Dibuat oleh **Muhammad Solihin**")
