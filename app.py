import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Risk Modelling Kecelakaan Kerja",
    layout="wide"
)

st.title("Risk Modelling Kecelakaan Kerja")
st.caption("Dashboard pemodelan risiko kecelakaan kerja berbasis Streamlit")

st.divider()

# =========================================================
# FASE 1 — DATA HISTORIS
# =========================================================
st.header("1. Data Historis Kecelakaan Kerja")

st.write(
    "Tabel di bawah ini berisi data historis kecelakaan kerja. "
    "Kamu bisa mengedit angka langsung di dalam tabel."
)

# Data awal (default) — sama seperti di Excel
default_data = pd.DataFrame({
    "Tahun": [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026],
    "Tidak Ada Korban": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    "Luka Ringan": [6, 1, 6, 1, 6, 5, 0, 0, 0],
    "Luka Berat": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    "Cacat Permanen": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    "Fatality": [2, 1, 0, 0, 0, 0, 0, 0, 0],
})

# Tabel editable
edited_data = st.data_editor(
    default_data,
    num_rows="dynamic",
    use_container_width=True,
    key="tabel_data_historis"
)

st.divider()

# =========================================================
# RATA-RATA (LAMBDA)
# =========================================================
st.header("2. Rata-Rata Kejadian per Tahun (Lambda)")

st.write(
    "Nilai Lambda dihitung dari rata-rata tiap kolom. "
    "Nilai ini akan dipakai sebagai dasar distribusi Poisson."
)

lambda_df = pd.DataFrame({
    "Kategori": [
        "Tidak Ada Korban",
        "Luka Ringan",
        "Luka Berat",
        "Cacat Permanen",
        "Fatality",
    ],
    "Lambda": [
        edited_data["Tidak Ada Korban"].mean(),
        edited_data["Luka Ringan"].mean(),
        edited_data["Luka Berat"].mean(),
        edited_data["Cacat Permanen"].mean(),
        edited_data["Fatality"].mean(),
    ],
})

lambda_df["Lambda"] = lambda_df["Lambda"].round(4)

st.dataframe(lambda_df, use_container_width=True, hide_index=True)

st.divider()

st.info("Fase 1 selesai. Selanjutnya: perhitungan probabilitas Poisson.")
