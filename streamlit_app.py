import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

# --------------------------------------
# KONFIGURASI HALAMAN
# --------------------------------------
st.set_page_config(
    page_title="Dashboard Open Transfer Order (CSV)",
    layout="wide",
)

st.title("📦 Dashboard Open Transfer Order PROD ➜ FG")
st.caption("Sumber: File CSV Open Transfer Order PROD to FG")

# --------------------------------------
# FUNGSI BACA CSV
# --------------------------------------
def _read_csv_flexible(file_or_buffer) -> pd.DataFrame:
    """
    Coba baca CSV dengan delimiter koma dulu,
    kalau error baru pakai delimiter semicolon (;).
    """
    try:
        df = pd.read_csv(file_or_buffer)
    except Exception:
        df = pd.read_csv(file_or_buffer, sep=";")
    return df


@st.cache_data
def load_data(file_or_path) -> pd.DataFrame:
    """
    Load data dari CSV dan rapikan tipe data + kolom turunan.
    Bisa menerima path (string/Path) atau UploadedFile.
    """
    df = _read_csv_flexible(file_or_path)

    # Nama kolom yang dipakai di app ini diambil dari struktur file kamu
    # Kalau di CSV beda tipis, bisa di-rename di sini.

    # Konversi tanggal
    if "Report Date" in df.columns:
        df["Report Date"] = pd.to_datetime(df["Report Date"], errors="coerce")

    # Pastikan kolom angka
    num_cols = [
        "Transfer Order Requested Quantity",
        "Transfer Order Shipped Quantity",
        "Transfer Order Delivered Quantity",
    ]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Isi NaN shipped & delivered dengan 0
    if "Transfer Order Shipped Quantity" in df.columns:
        df["Transfer Order Shipped Quantity"] = df["Transfer Order Shipped Quantity"].fillna(0)
    else:
        df["Transfer Order Shipped Quantity"] = 0

    if "Transfer Order Delivered Quantity" in df.columns:
        df["Transfer Order Delivered Quantity"] = df["Transfer Order Delivered Quantity"].fillna(0)
    else:
        df["Transfer Order Delivered Quantity"] = 0

    # Kolom turunan open qty
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
    "Upload file CSV Transfer Order",
    type=["csv"],
    help="Export dulu Excel ke CSV lalu upload di sini.",
)

# OPTIONAL: path default ke CSV di server/lokal
default_path = Path("Open Transfer Order PROD to FG 201125.csv")

if uploaded_file is not None:
    df = load_data(uploaded_file)
elif default_path.exists():
    st.sidebar.info(f"Menggunakan file lokal: {default_path.name}")
    df = load_data(default_path)
else:
    st.info("Silakan upload file CSV di sidebar untuk memulai.")
    st.stop()

# --------------------------------------
# KONSTANTA NAMA KOLOM
# --------------------------------------
dest_col = "Inventory Destination Organization Name"
source_col = "Source Inventory Organization Name"
uom_col = "Item Primary Unit of Measure"
item_col = "Item"
status_col = "Transfer Order Line Status"
to_number_col = "Transfer Order Number"

# --------------------------------------
# SIDEBAR - FILTER
# --------------------------------------
st.sidebar.header("🔍 Filter Data")

# Filter tanggal
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
dest_options = sorted(df[dest_col].dropna().unique())
selected_dest = st.sidebar.multiselect(
    "Destination Organization",
    options=dest_options,
    default=dest_options,
)

# Source Org
source_options = sorted(df[source_col].dropna().unique())
selected_source = st.sidebar.multiselect(
    "Source Organization",
    options=source_options,
    default=source_options,
)

# Unit of Measure (UOM)
uom_options = sorted(df[uom_col].dropna().unique())
selected_uom = st.sidebar.multiselect(
    "Unit of Measure (UOM)",
    options=uom_options,
    default=uom_options,
)

# Item
item_options = sorted(df[item_col].dropna().unique())
selected_items = st.sidebar.multiselect(
    "Item (optional)",
    options=item_options,
    default=[],
    help="Kosongkan jika ingin semua item.",
)

# Line Status (kalau ada)
if status_col in df.columns:
    status_options = sorted(df[status_col].dropna().unique())
    selected_status = st.sidebar.multiselect(
        "Line Status",
        options=status_options,
        default=status_options,
    )
else:
    status_options = []
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
    mask &= df[dest_col].isin(selected_dest)

# Filter source
if selected_source:
    mask &= df[source_col].isin(selected_source)

# Filter UOM
if selected_uom:
    mask &= df[uom_col].isin(selected_uom)

# Filter item (jika dipilih)
if selected_items:
    mask &= df[item_col].isin(selected_items)

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

num_to = filtered[to_number_col].nunique()
num_lines = len(filtered)
total_req = filtered["Transfer Order Requested Quantity"].sum()
total_ship = filtered["Transfer Order Shipped Quantity"].sum()
total_del = filtered["Transfer Order Delivered Quantity"].sum()
open_req = total_req - total_del
open_ship = total_ship - total_del

col1.metric("Jumlah Transfer Order (unik)", f"{num_to}")
col2.metric("Jumlah Line", f"{num_lines}")
col3.metric("Total Qty Requested (ALL UOM)", f"{total_req:,.2f}")
col4.metric("Total Qty Shipped (ALL UOM)", f"{total_ship:,.2f}")
col5.metric("Total Qty Delivered (ALL UOM)", f"{total_del:,.2f}")
col6.metric("Total Open Qty (Req - Deliv)", f"{open_req:,.2f}")

st.caption(
    "Catatan: Total Qty di atas adalah penjumlahan semua UOM. "
    "Lihat tabel ringkasan per UOM di bawah untuk angka yang lebih bermakna."
)

# --------------------------------------
# STATUS TRANSFER ORDER (HEADER-LEVEL)
# --------------------------------------
st.markdown("#### 📑 Status Transfer Order (berdasarkan nomor TO)")

def map_to_header_status(series: pd.Series) -> str:
    """
    Mapping status header TO dari gabungan status line.
    Logika sederhana:
    - Kalau ADA line mengandung kata 'open' -> Open
    - ELSE kalau ADA line mengandung 'cancel' -> Canceled
    - ELSE kalau ADA line mengandung 'close' -> Closed
    - ELSE -> Unknown
    (case-insensitive, berbasis substring)
    """
    statuses = (
        series.dropna()
        .astype(str)
        .str.lower()
        .unique()
    )
    if len(statuses) == 0:
        return "Unknown"

    if any("open" in s for s in statuses):
        return "Open"
    if any("cancel" in s for s in statuses):
        return "Canceled"
    if any("clos" in s for s in statuses):  # cover 'close', 'closed'
        return "Closed"

    return "Unknown"


if status_col in filtered.columns:
    header_status = (
        filtered.groupby(to_number_col)[status_col]
        .apply(map_to_header_status)
        .reset_index(name="TO Status")
    )

    # Hitung jumlah TO per status
    status_counts = header_status["TO Status"].value_counts().reset_index()
    status_counts.columns = ["TO Status", "Jumlah TO"]

    # Metric per status utama
    open_to = int((header_status["TO Status"] == "Open").sum())
    closed_to = int((header_status["TO Status"] == "Closed").sum())
    canceled_to = int((header_status["TO Status"] == "Canceled").sum())
    unknown_to = int((header_status["TO Status"] == "Unknown").sum())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("TO Open", f"{open_to}")
    c2.metric("TO Closed", f"{closed_to}")
    c3.metric("TO Canceled", f"{canceled_to}")
    c4.metric("TO Unknown/Lain", f"{unknown_to}")

    with st.expander("Detail status per nomor TO"):
        st.dataframe(header_status, use_container_width=True)

    with st.expander("Rekap jumlah TO per status"):
        st.dataframe(status_counts, use_container_width=True)
else:
    st.info("Kolom status line (Transfer Order Line Status) tidak ditemukan di data.")

st.divider()

# --------------------------------------
# RINGKASAN PER UOM
# --------------------------------------
st.markdown("#### 🔢 Ringkasan per Unit of Measure (UOM)")

kpi_uom = (
    filtered.groupby(uom_col, as_index=False)
    .agg(
        Total_Requested=("Transfer Order Requested Quantity", "sum"),
        Total_Shipped=("Transfer Order Shipped Quantity", "sum"),
        Total_Delivered=("Transfer Order Delivered Quantity", "sum"),
    )
    .sort_values("Total_Requested", ascending=False)
)
st.dataframe(kpi_uom, use_container_width=True)

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

    chart_data = by_date.set_index("Report Date")[["Total_Requested", "Total_Shipped"]]
    st.line_chart(chart_data)
else:
    st.info("Kolom Report Date kosong / tidak valid, tren tidak dapat ditampilkan.")

st.divider()

# --------------------------------------
# DISTRIBUSI PER DESTINATION ORG (TOTAL + PER UOM)
# --------------------------------------
st.subheader("🏭 Distribusi per Destination Organization")

# Total per destination (ALL UOM)
by_dest = (
    filtered.groupby(dest_col, as_index=False)
    .agg(
        Total_Requested=("Transfer Order Requested Quantity", "sum"),
        Total_Shipped=("Transfer Order Shipped Quantity", "sum"),
        Total_Delivered=("Transfer Order Delivered Quantity", "sum"),
    )
    .sort_values("Total_Requested", ascending=False)
)

top_n_dest = st.slider("Tampilkan Top N Destination Org", min_value=3, max_value=20, value=5)

top_dest_names = by_dest[dest_col].head(top_n_dest).tolist()

st.markdown("##### 🔹 Total Requested per Destination (ALL UOM)")
st.bar_chart(
    by_dest.set_index(dest_col)["Total_Requested"].head(top_n_dest)
)

with st.expander("Lihat tabel total per Destination Organization"):
    st.dataframe(by_dest, use_container_width=True)

# Breakdown per Destination & UOM
st.markdown("##### 🔹 Breakdown Requested per Destination & UOM")

by_dest_uom = (
    filtered.groupby([dest_col, uom_col], as_index=False)
    .agg(
        Total_Requested=("Transfer Order Requested Quantity", "sum"),
        Total_Shipped=("Transfer Order Shipped Quantity", "sum"),
        Total_Delivered=("Transfer Order Delivered Quantity", "sum"),
    )
)

# Ambil hanya top N destination saja untuk chart, supaya tidak terlalu ramai
by_dest_uom_top = by_dest_uom[by_dest_uom[dest_col].isin(top_dest_names)]

if not by_dest_uom_top.empty:
    # Pivot: index = destination, kolom = UOM, value = Total_Requested
    pivot_dest_uom = (
        by_dest_uom_top
        .pivot(index=dest_col, columns=uom_col, values="Total_Requested")
        .fillna(0)
        .sort_index()
    )
    st.bar_chart(pivot_dest_uom)
else:
    st.info("Tidak ada data untuk kombinasi Destination & UOM pada filter ini.")

with st.expander("Lihat tabel lengkap per Destination & UOM"):
    st.dataframe(
        by_dest_uom.sort_values([dest_col, uom_col]),
        use_container_width=True
    )

st.divider()

# --------------------------------------
# TOP ITEM (DENGAN UOM)
# --------------------------------------
st.subheader("🍘 Top Item berdasarkan Qty Requested (per UOM Item)")

by_item = (
    filtered.groupby([item_col, "Item Description", uom_col], as_index=False)
    .agg(
        Total_Requested=("Transfer Order Requested Quantity", "sum"),
        Total_Shipped=("Transfer Order Shipped Quantity", "sum"),
        Total_Delivered=("Transfer Order Delivered Quantity", "sum"),
    )
    .sort_values("Total_Requested", ascending=False)
)

top_n_item = st.slider(
    "Tampilkan Top N Item",
    min_value=5,
    max_value=30,
    value=10,
    key="top_item"
)
top_item_df = by_item.head(top_n_item)

chart_item = top_item_df.copy()
chart_item["Label"] = chart_item.apply(
    lambda row: f"{row[item_col]} ({row[uom_col]})", axis=1
)

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

csv_download = filtered.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "⬇️ Download data ter-filter (CSV)",
    data=csv_download,
    file_name="filtered_transfer_order.csv",
    mime="text/csv",
)
