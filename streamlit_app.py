import streamlit as st
import pandas as pd

st.title("Ekstraksi Kode Titik ke Kolom")

input_text = st.text_area("Masukkan kode di sini:", height=300)

if st.button("Ekstrak"):
    if input_text.strip():
        # Pisahkan per baris dan hilangkan baris kosong
        lines = [line.strip() for line in input_text.splitlines() if line.strip()]

        # Pisahkan berdasarkan titik
        data = [line.split('.') for line in lines]

        # Buat nama kolom otomatis
        max_cols = max(len(row) for row in data)
        columns = [f"col{i+1}" for i in range(max_cols)]

        # Buat DataFrame dan tampilkan
        df = pd.DataFrame(data, columns=columns)
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Masukkan teks terlebih dahulu!")
