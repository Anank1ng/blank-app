import streamlit as st
import pandas as pd

# Fungsi untuk melakukan data cleansing
def compare_data(main_file, comparison_file, vlookup_key):
    # Membaca file Excel
    main_df = pd.read_excel(main_file)
    comparison_df = pd.read_excel(comparison_file)

    # Menampilkan preview dari kedua file
    st.write("Preview Data Utama:")
    st.write(main_df.head())
    st.write("Preview Data Pembanding:")
    st.write(comparison_df.head())

    # Memastikan kolom VLOOKUP key ada di kedua DataFrame
    if vlookup_key not in main_df.columns or vlookup_key not in comparison_df.columns:
        st.error(f"Key '{vlookup_key}' tidak ditemukan di salah satu file.")
        return

    # Membandingkan data berdasarkan key yang diberikan
    comparison_result = main_df.merge(comparison_df, on=vlookup_key, how='outer', indicator=True)

    # Menampilkan perbedaan
    st.write("Perbandingan Data:")
    st.write(comparison_result)

    # Menampilkan data yang berbeda
    st.write("Data yang ada di file utama tetapi tidak ada di file pembanding:")
    st.write(comparison_result[comparison_result['_merge'] == 'left_only'])

    st.write("Data yang ada di file pembanding tetapi tidak ada di file utama:")
    st.write(comparison_result[comparison_result['_merge'] == 'right_only'])

# Streamlit UI
st.title("Data Cleansing dan Perbandingan Excel")

# Mengunggah file Excel
main_file = st.file_uploader("Unggah File Excel Utama", type=["xlsx"])
comparison_file = st.file_uploader("Unggah File Excel Pembanding", type=["xlsx"])

# Input key untuk VLOOKUP
vlookup_key = st.text_input("Masukkan Key untuk Perbandingan (VLOOKUP Key)", "")

if main_file and comparison_file and vlookup_key:
    compare_data(main_file, comparison_file, vlookup_key)
