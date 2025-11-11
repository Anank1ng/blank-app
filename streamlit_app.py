import streamlit as st
import pandas as pd
from io import BytesIO

st.title("📘 Penggabung Multi File Excel Berdasarkan Sheet (Fleksibel)")

st.write("""
Unggah **3 file Excel atau lebih**, lalu pilih **sheet dari masing-masing file**
yang ingin digabungkan. Semua data akan digabung jadi satu file Excel.
""")

# Upload multiple Excel files
uploaded_files = st.file_uploader(
    "Unggah File Excel (minimal 3)", 
    type=["xlsx"], 
    accept_multiple_files=True
)

if uploaded_files and len(uploaded_files) >= 3:
    selected_sheets = {}

    # Tampilkan opsi sheet untuk tiap file
    st.write("### Pilih Sheet dari Tiap File")
    for file in uploaded_files:
        xls = pd.ExcelFile(file)
        sheet = st.selectbox(
            f"Pilih sheet dari: **{file.name}**", 
            xls.sheet_names,
            key=file.name
        )
        selected_sheets[file.name] = (file, sheet)

    # Tombol gabungkan
    if st.button("Gabungkan Semua Sheet Terpilih"):
        combined_data = []
        for filename, (file, sheetname) in selected_sheets.items():
            try:
                df = pd.read_excel(file, sheet_name=sheetname)
                df["Sumber_File"] = filename
                df["Sheet_Asal"] = sheetname
                combined_data.append(df)
            except Exception as e:
                st.warning(f"⚠️ Gagal membaca sheet '{sheetname}' dari file {filename}: {e}")

        if combined_data:
            result = pd.concat(combined_data, ignore_index=True)
            st.success(f"✅ Berhasil menggabungkan {len(combined_data)} sheet!")
            st.dataframe(result)

            # Simpan hasil ke buffer agar bisa diunduh
            buffer = BytesIO()
            result.to_excel(buffer, index=False)
            buffer.seek(0)

            st.download_button(
                label="⬇️ Unduh Hasil Gabungan",
                data=buffer,
                file_name="hasil_gabungan_semua_sheet.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("Tidak ada data yang berhasil digabung. Periksa pilihan sheet.")
else:
    st.info("Silakan unggah minimal 3 file Excel terlebih dahulu.")
