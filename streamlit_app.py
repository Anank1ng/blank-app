import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

# --------------------------------------
# KONFIGURASI HALAMAN
# --------------------------------------
st.set_page_config(
    page_title="Dashboard Open Transfer Order",
    layout="wide",
)

st.title("📦 Dashboard Open Transfer Order PROD ➜ FG")
st.caption("Sumber: File Excel Open Transfer Order PROD to FG")

# --------------------------------------
# FUNGSI LOAD DATA
# --------------------------------------
@st.cache_data
def load_data(file) -> pd.DataFrame:
    df = pd.read_excel(file)

    # Pastikan nama kolom sesuai dan tipe data rapih
    # Jika ada nama yang beda, bisa di-rename di sini.
    # Contoh:
    # df = df.rename(columns={"Report date": "Report Date"})
    # (sementara diasumsikan sama dengan file yang kamu kirim)

    # Konversi tanggal
    if "Report Date" in df.columns:
        df["Report Date"] = pd.to_datetime(df["Report Date"], errors="coerce")

    # Pastikan numeric column diperlakukan sebagai angka
    num_cols = [
        "Transfer Order Requested Quantity",
        "Transfer Order Shipped Quantity",
        "Transfer Order Delivered Quantity",
    ]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Isi NaN delivered & shipped dengan 0 untuk perhitungan
    df["Transfer Order Shipped Quantity"] = df["Transfer Order Shipped Quantity"].fillna(0)
    df["Transfer Order Delivered Quantity"] = df["Transfer Order Delivered Quantity"].fillna(0)

    # Tambah kolom turunan
    df["Open_vs_Requested"] = (
        df["Transfer Order Requested Quantity"] - df["Transfer Order Delivered Quantity"]
    )
    df["Open_vs_Shipped"] = (
        df["Transfer Order Shipped Quantity"] - df["Transfer Order Delivered Quantity"]
    )

    return df


# --------------------------------------
# INPUT FILE
# --------------------------------------
st.sidebar.header("📁 Data Source")

uploaded_file = st.sidebar.file_uploader(
    "Upload file Excel Transfer Order",
    type=["xlsx", "xls"],
    help="Pilih file yang berisi data transfer order.",
)

# OPTIONAL: path default (kalau mau langsung pakai file lokal)
default_path = Path("Open Transfer Order PROD to FG 201125.xlsx")
df = None

if uploaded_file is not None:
    df = load_data(uploaded_file)
elif default_path.exists():
    st.sidebar.info(f"Menggunakan file lokal: {default_path.name}")
    df = load_data(default_path)
else:
    st.info("Silakan upload file Excel di sidebar untuk memulai.")
    st.stop()

# --------------------------------------
# SIDEBAR - FILTER
# --------------------------------------
st.sidebar.header("🔍 Filter Data")

# Date range
if "Report Date" in df.columns and df["Report Date"].notna().any():
    min_date = df["Report Date"].min().date()
    max_date = df["Report Date"].max().date()
    date_range = st.sidebar.date_input(
        "Rentang Report Date",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
else:
    date_range = None

# Destination Org
dest_options = sorted(df["Inventory Destination Organization Name"].dropna().unique())
selected_dest = st.sidebar.multiselect(
    "Destination Organization",
    options=dest_options,
    default=dest_options,
)

# Source Org
source_options = sorted(df["Source Inventory Organization Name"].dropna().unique())
selected_source = st.sidebar.multiselect(
    "Source Organization",
    options=source_options,
    default=source_options,
)

# Item
item_options = sorted(df["Item"].dropna().unique())
selected_items = st.sidebar.multiselect(
    "Item (optional)",
    options=item_options,
    default=[],
    help="Kosongkan jika ingin semua item.",
)

# Line Status (kalau ada)
status_col = "Transfer Order Line Status"
if status_col in df.columns:
    status_options = sorted(df[status_col].dropna().unique())
    selected_status = st.sidebar.multiselect(
        "Line Status",
        options=status_options,
        default=status_options,
    )
else:
    selected_status = None

# --------------------------------------
# APLIKASI FILTER KE DATA
# --------------------------------------
mask = np.ones(len(df), dtype=bool)

# Filter tanggal
if date_range is not None and len(date_range) == 2:
    start_date, end_date = date_range
    if start_date and end_date:
        mask &= (df["Report Date"].dt.date >= start_date) & (
            df["Report Date"].dt.date <= end_date
        )

# Filter destination
if selected_dest:
    mask &= df["Inventory Destination Organization Name"].isin(selected_dest)

# Filter source
if selected_source:
    mask &= df["Source Inventory Organization Name"].isin(selected_source)

# Filter item (jika dipilih)
if selected_items:
    mask &= df["Item"].isin(selected_items)

# Filter status
if selected_status is not None and selected_status:
    mask &= df[status_col].isin(selected_status)

filtered = df.loc[mask].copy()

if filtered.empty:
    st.warning("Tidak ada data untuk kombinasi filter ini. Coba longgarkan filter.")
    st.stop()

# --------------------------------------
# KPI SECTION
# --------------------------------------
st.subheader("📌 Ringkasan KPI (berdasarkan filter)")

col1, col2, col3, col4 = st.columns(4)
col5, col6 = st.columns(2)

num_to = filtered["Transfer Order Number"].nunique()
num_lines = len(filtered)
total_req = filtered["Transfer Order Requested Quantity"].sum()
total_ship = filtered["Transfer Order Shipped Quantity"].sum()
total_del = filtered["Transfer Order Delivered Quantity"].sum()
open_req = total_req - total_del
open_ship = total_ship - total_del

col1.metric("Jumlah Transfer Order (unik)", f"{num_to}")
col2.metric("Jumlah Line", f"{num_lines}")
col3.metric("Total Qty Requested", f"{total_req:,.0f}")
col4.metric("Total Qty Shipped", f"{total_ship:,.2f}")
col5.metric("Total Qty Delivered", f"{total_del:,.2f}")
col6.metric("Total Open Qty (Req - Deliv)", f"{open_req:,.2f}")

st.divider()

# --------------------------------------
# TREND PER TANGGAL
# --------------------------------------
st.subheader("📈 Tren Requested vs Shipped per Report Date")

if filtered["Report Date"].notna().any():
    by_date = (
        filtered.groupby("Report Date", as_index=False)
        .agg(
            Total_Requested=("Transfer Order Requested Quantity", "sum"),
            Total_Shipped=("Transfer Order Shipped Quantity", "sum"),
            Total_Delivered=("Transfer Order Delivered Quantity", "sum"),
        )
        .sort_values("Report Date")
    )

    # Pakai Streamlit built-in line_chart
    chart_data = by_date.set_index("Report Date")[["Total_Requested", "Total_Shipped"]]
    st.line_chart(chart_data)
else:
    st.info("Kolom Report Date kosong / tidak valid, tren tidak dapat ditampilkan.")

st.divider()

# --------------------------------------
# DISTRIBUSI DESTINATION ORG
# --------------------------------------
st.subheader("🏭 Distribusi per Destination Organization")

by_dest = (
    filtered.groupby("Inventory Destination Organization Name", as_index=False)
    .agg(
        Total_Requested=("Transfer Order Requested Quantity", "sum"),
        Total_Shipped=("Transfer Order Shipped Quantity", "sum"),
        Total_Delivered=("Transfer Order Delivered Quantity", "sum"),
    )
    .sort_values("Total_Requested", ascending=False)
)

top_n_dest = st.slider("Tampilkan Top N Destination Org", min_value=3, max_value=20, value=5)
st.bar_chart(
    by_dest.set_index("Inventory Destination Organization Name")[
        "Total_Requested"
    ].head(top_n_dest)
)

with st.expander("Lihat tabel lengkap per Destination Organization"):
    st.dataframe(by_dest, use_container_width=True)

st.divider()

# --------------------------------------
# TOP ITEM
# --------------------------------------
st.subheader("🍘 Top Item berdasarkan Qty Requested")

by_item = (
    filtered.groupby(["Item", "Item Description"], as_index=False)
    .agg(
        Total_Requested=("Transfer Order Requested Quantity", "sum"),
        Total_Shipped=("Transfer Order Shipped Quantity", "sum"),
        Total_Delivered=("Transfer Order Delivered Quantity", "sum"),
    )
    .sort_values("Total_Requested", ascending=False)
)

top_n_item = st.slider("Tampilkan Top N Item", min_value=5, max_value=30, value=10, key="top_item")
top_item_df = by_item.head(top_n_item)

# Untuk bar chart, pakai index = Item (bisa dikombinasi dengan description kalau mau)
chart_item = top_item_df.copy()
chart_item["Label"] = chart_item["Item"]  # bisa diganti f"{Item} - {Desc}" kalau mau
st.bar_chart(
    chart_item.set_index("Label")["Total_Requested"]
)

with st.expander("Lihat tabel lengkap per Item"):
    st.dataframe(by_item, use_container_width=True)

st.divider()

# --------------------------------------
# DATA DETAIL
# --------------------------------------
st.subheader("📋 Data Detail (sudah ter-filter)")

st.dataframe(filtered, use_container_width=True, height=400)

# Tombol download data ter-filter
csv = filtered.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "⬇️ Download data ter-filter (CSV)",
    data=csv,
    file_name="filtered_transfer_order.csv",
    mime="text/csv",
)
