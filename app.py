import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# =========================================================
# KONFIGURASI HALAMAN
# =========================================================
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

default_data = pd.DataFrame({
    "Tahun": [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026],
    "Tidak Ada Korban": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    "Luka Ringan": [6, 1, 6, 1, 6, 5, 0, 0, 0],
    "Luka Berat": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    "Cacat Permanen": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    "Fatality": [2, 1, 0, 0, 0, 0, 0, 0, 0],
})

edited_data = st.data_editor(
    default_data,
    num_rows="dynamic",
    use_container_width=True,
    key="tabel_data_historis"
)

st.divider()

# =========================================================
# FASE 1B — RATA-RATA (LAMBDA)
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

# =========================================================
# FASE 2 — PROBABILITAS POISSON
# =========================================================
st.header("3. Probabilitas Poisson")

st.write(
    "Probabilitas dihitung menggunakan distribusi Poisson "
    "berdasarkan nilai Lambda tiap kategori dampak."
)

konfigurasi = pd.DataFrame({
    "Kategori": [
        "Tidak Ada Korban",
        "Luka Ringan",
        "Luka Berat",
        "Cacat Permanen",
        "Fatality",
    ],
    "Tingkat Dampak": [
        "Sangat Rendah",
        "Rendah",
        "Moderat",
        "Tinggi",
        "Sangat Tinggi",
    ],
    "Dampak Atas": [5, 5, 5, 5, 2],
    "Dampak Bawah": [1, 1, 1, 1, 1],
})

prob_df = konfigurasi.merge(lambda_df, on="Kategori")

def hitung_probabilitas(lam, atas, bawah):
    if lam <= 0:
        return 0.0
    return poisson.cdf(atas, lam) - poisson.cdf(bawah - 1, lam)

prob_df["Probabilitas"] = prob_df.apply(
    lambda row: hitung_probabilitas(
        row["Lambda"], row["Dampak Atas"], row["Dampak Bawah"]
    ),
    axis=1
)

prob_df["Probabilitas"] = prob_df["Probabilitas"].round(4)

st.dataframe(
    prob_df[["Kategori", "Lambda", "Dampak Bawah", "Dampak Atas", "Probabilitas"]],
    use_container_width=True,
    hide_index=True
)

st.divider()

st.subheader("Grafik Probabilitas per Kategori")

st.bar_chart(
    prob_df.set_index("Kategori")["Probabilitas"],
    use_container_width=True
)

st.divider()

# =========================================================
# FASE 3 — MATRIKS RISIKO 5x5
# =========================================================
st.header("4. Matriks Risiko 5x5")

st.write(
    "Probabilitas dikonversi menjadi kategori kemungkinan, "
    "lalu dipetakan ke matriks risiko 5x5 untuk mendapatkan "
    "level risiko dan skala risiko."
)

# --- Fungsi kategori kemungkinan ---
def kategori_kemungkinan(p):
    if p < 0.2:
        return "Sangat Jarang Terjadi"
    elif p < 0.4:
        return "Jarang Terjadi"
    elif p < 0.6:
        return "Bisa Terjadi"
    elif p < 0.8:
        return "Sangat Mungkin Terjadi"
    else:
        return "Hampir Pasti Terjadi"

prob_df["Kemungkinan"] = prob_df["Probabilitas"].apply(kategori_kemungkinan)

# --- Matriks level risiko (sesuai Excel) ---
# Baris: kemungkinan, Kolom: tingkat dampak
# Urutan kemungkinan: Sangat Jarang, Jarang, Bisa, Sangat Mungkin, Hampir Pasti
# Urutan dampak: Sangat Rendah, Rendah, Moderat, Tinggi, Sangat Tinggi
matriks_level = [
    ["Low", "Low", "Low to Moderate", "Moderate", "High"],
    ["Low", "Low to Moderate", "Low to Moderate", "Moderate to High", "High"],
    ["Low", "Low to Moderate", "Moderate", "Moderate to High", "High"],
    ["Low", "Low to Moderate", "Moderate", "Moderate to High", "High"],
    ["Low to Moderate", "Moderate", "Moderate to High", "High", "High"],
]

# --- Matriks skala risiko (sesuai Excel) ---
matriks_skala = [
    [1, 5, 10, 15, 20],
    [2, 6, 11, 16, 21],
    [3, 8, 13, 18, 23],
    [4, 9, 14, 19, 24],
    [7, 12, 17, 22, 25],
]

urutan_kemungkinan = [
    "Sangat Jarang Terjadi",
    "Jarang Terjadi",
    "Bisa Terjadi",
    "Sangat Mungkin Terjadi",
    "Hampir Pasti Terjadi",
]

urutan_dampak = [
    "Sangat Rendah",
    "Rendah",
    "Moderat",
    "Tinggi",
    "Sangat Tinggi",
]

def level_risiko(kemungkinan, dampak):
    i = urutan_kemungkinan.index(kemungkinan)
    j = urutan_dampak.index(dampak)
    return matriks_level[i][j]

def skala_risiko(kemungkinan, dampak):
    i = urutan_kemungkinan.index(kemungkinan)
    j = urutan_dampak.index(dampak)
    return matriks_skala[i][j]

prob_df["Level Risiko"] = prob_df.apply(
    lambda row: level_risiko(row["Kemungkinan"], row["Tingkat Dampak"]),
    axis=1
)

prob_df["Skala Risiko"] = prob_df.apply(
    lambda row: skala_risiko(row["Kemungkinan"], row["Tingkat Dampak"]),
    axis=1
)

st.subheader("Hasil Pemetaan Risiko Aktual")

st.dataframe(
    prob_df[[
        "Kategori",
        "Tingkat Dampak",
        "Probabilitas",
        "Kemungkinan",
        "Level Risiko",
        "Skala Risiko",
    ]],
    use_container_width=True,
    hide_index=True
)

st.divider()

st.info("Fase 3 selesai. Selanjutnya: visualisasi matriks risiko.")
