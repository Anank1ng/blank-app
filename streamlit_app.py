# app.py
import io
import pandas as pd
import streamlit as st

st.set_page_config(page_title="VLOOKUP Tanpa Upload", page_icon="🔎", layout="centered")
st.title("🔎 VLOOKUP: Input Manual (Tanpa Upload)")

st.write("Tempel (paste) data kamu di bawah. Boleh berupa CSV/TSV atau dipisah koma/tab/spasi/baris.")

with st.sidebar:
    st.header("⚙️ Pengaturan")
    not_found_choice = st.selectbox(
        "Jika tidak ketemu, tampilkan:",
        options=["Tidak ada", "NA", "False"],
        index=0
    )
    trim_space = st.checkbox("Trim spasi & samakan huruf (case-insensitive)", value=True)
    drop_duplicates_master = st.checkbox("Ambil baris pertama jika kunci duplikat di master", value=True)

# =========================
# Parsers
# =========================
def smart_read_table(text: str, expected_cols=None):
    """
    Terima teks, coba parse ke DataFrame.
    - Mencoba pemisah: ',', '\t', ';', '|', ' ' (multi-spasi)
    - Mendeteksi header jika cocok
    - expected_cols: kalau diberikan (int), dan tidak ada header, buat nama kolom generik
    """
    text = text.strip()
    if not text:
        return pd.DataFrame()

    # Kandidat separator
    seps = [",", "\t", ";", "|"]
    df = None

    # Coba sebagai CSV dengan beberapa pemisah
    for sep in seps:
        try:
            df_try = pd.read_csv(io.StringIO(text), sep=sep)
            if df_try.shape[1] >= 1:
                df = df_try
                break
        except Exception:
            pass

    # Jika belum berhasil, coba whitespace
    if df is None:
        try:
            df = pd.read_csv(io.StringIO(text), sep=r"\s+", engine="python", header=None)
        except Exception:
            # fallback: tiap baris jadi satu kolom
            rows = [line for line in text.splitlines() if line.strip()]
            df = pd.DataFrame(rows, columns=["col1"])

    # Jika expected_cols diberikan dan kolom lebih sedikit, tambahkan kolom kosong
    if expected_cols is not None and df.shape[1] < expected_cols:
        for i in range(expected_cols - df.shape[1]):
            df[f"col{df.shape[1]+1}"] = pd.NA

    # Jika tidak ada header yang jelas dan expected_cols tersedia,
    # berikan nama generik
    if expected_cols is not None and df.columns.astype(str).str.startswith("Unnamed").all():
        df.columns = [f"col{i+1}" for i in range(df.shape[1])]

    return df

# =========================
# Input Areas
# =========================
col1, col2 = st.columns(2)
with col1:
    tarikan_text = st.text_area(
        "✍️ Data Tarikan (1 kolom kunci)",
        height=220,
        placeholder="Contoh:\n12345\n67890\nABC01\nABC02"
    )
with col2:
    master_text = st.text_area(
        "✍️ Data Master (2 kolom: kunci, nilai)",
        height=220,
        placeholder="Contoh CSV:\nkey,value\n12345,Nama A\n67890,Nama B\nABC02,Nama C"
    )

# Parse
df_tarikan = smart_read_table(tarikan_text) if tarikan_text.strip() else pd.DataFrame()
df_master  = smart_read_table(master_text) if master_text.strip() else pd.DataFrame()

# Tampilkan pratinjau
if not df_tarikan.empty:
    st.subheader("🔹 Pratinjau Data Tarikan")
    st.dataframe(df_tarikan.head(10), use_container_width=True)
if not df_master.empty:
    st.subheader("🔹 Pratinjau Data Master")
    st.dataframe(df_master.head(10), use_container_width=True)

if not df_tarikan.empty and not df_master.empty:
    st.markdown("---")
    st.subheader("🔧 Pilih Kolom")

    # Pilihan kolom dinamis
    tarikan_key_col = st.selectbox("Kolom kunci pada **Data Tarikan**", df_tarikan.columns, index=0)
    # Untuk master, minimal 2 kolom
    if df_master.shape[1] < 2:
        st.error("Data Master harus punya minimal 2 kolom (kunci & nilai). Tambahkan kolom nilai.")
        st.stop()

    master_key_col  = st.selectbox("Kolom kunci pada **Data Master**", df_master.columns, index=0)
    value_candidates = [c for c in df_master.columns if c != master_key_col]
    master_value_col = st.selectbox("Kolom nilai yang diambil dari **Data Master**", value_candidates, index=0)

    # Salin aman
    t = df_tarikan[[tarikan_key_col]].copy()
    m = df_master[[master_key_col, master_value_col]].copy()

    # Normalisasi sesuai opsi
    if trim_space:
        t["_key"] = t[tarikan_key_col].astype(str).str.strip().str.lower()
        m["_key"] = m[master_key_col].astype(str).str.strip().str.lower()
    else:
        t["_key"] = t[tarikan_key_col]
        m["_key"] = m[master_key_col]

    # Hilangkan duplikat kunci di master kalau dipilih
    if drop_duplicates_master:
        m = m.drop_duplicates(subset=["_key"], keep="first")

    # Merge gaya VLOOKUP (left)
    merged = t.merge(m[["_key", master_value_col]], on="_key", how="left")

    # Atur nilai ketika tidak ketemu
    if not_found_choice == "Tidak ada":
        fill_val = "Tidak ada"
    elif not_found_choice == "NA":
        fill_val = pd.NA
    else:
        fill_val = False

    merged[master_value_col] = merged[master_value_col].fillna(fill_val)

    # Hasil akhir: 2 kolom
    result = pd.DataFrame({
        str(tarikan_key_col): df_tarikan[tarikan_key_col],
        str(master_value_col): merged[master_value_col]
    })

    st.subheader("✅ Hasil (2 Kolom)")
    st.dataframe(result, use_container_width=True)

    # Unduh CSV
    csv_buf = io.StringIO()
    result.to_csv(csv_buf, index=False)
    st.download_button(
        "💾 Download Hasil CSV",
        data=csv_buf.getvalue(),
        file_name="hasil_vlookup_2kolom.csv",
        mime="text/csv"
    )

    # Ringkasan
    total = len(result)
    if not_found_choice == "Tidak ada":
        tidak_ketemu = (result.iloc[:, 1] == "Tidak ada").sum()
    elif not_found_choice == "NA":
        tidak_ketemu = result.iloc[:, 1].isna().sum()
    else:
        tidak_ketemu = (result.iloc[:, 1] == False).sum()

    st.caption(f"Baris: {total} • Tidak ketemu: {tidak_ketemu}")

else:
    st.info("Isi **Data Tarikan** dan **Data Master** untuk memulai. Minimal 1 kolom di tarikan, 2 kolom di master.")
