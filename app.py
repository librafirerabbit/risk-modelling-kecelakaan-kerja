import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
import plotly.graph_objects as go

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
    "Kode": ["K1", "K2", "K3", "K4", "K5"],
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
    prob_df[["Kode", "Kategori", "Lambda", "Dampak Bawah", "Dampak Atas", "Probabilitas"]],
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
    "lalu dipetakan ke matriks risiko 5x5."
)

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

matriks_level = [
    ["Low", "Low", "Low to Moderate", "Moderate", "High"],
    ["Low", "Low to Moderate", "Low to Moderate", "Moderate to High", "High"],
    ["Low", "Low to Moderate", "Moderate", "Moderate to High", "High"],
    ["Low", "Low to Moderate", "Moderate", "Moderate to High", "High"],
    ["Low to Moderate", "Moderate", "Moderate to High", "High", "High"],
]

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
        "Kode",
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

# =========================================================
# FASE 4 — HEATMAP MATRIKS RISIKO (Warna & Legenda Baru)
# =========================================================
st.header("5. Heatmap Matriks Risiko")

st.write(
    "Visualisasi matriks risiko 5x5. Angka di dalam kotak adalah "
    "skala risiko. Posisi kategori aktual ditandai dengan lingkaran putih."
)

# Warna diskrit sesuai skala risiko
# 1-5 Low (hijau tua)
# 6-10 Low to Moderate (hijau muda)
# 11-15 Moderate (kuning)
# 16-19 Moderate to High (oranye)
# 20-25 High (merah-oranye)

def warna_skala(nilai):
    if 1 <= nilai <= 5:
        return "#2ecc71"   # Low
    elif 6 <= nilai <= 10:
        return "#a8d08d"   # Low to Moderate
    elif 11 <= nilai <= 15:
        return "#ffd966"   # Moderate
    elif 16 <= nilai <= 19:
        return "#f4b183"   # Moderate to High
    else:
        return "#e06666"   # High

# Buat matriks warna untuk heatmap
warna_matriks = []
for i in range(5):
    baris = []
    for j in range(5):
        baris.append(warna_skala(matriks_skala[i][j]))
    warna_matriks.append(baris)

# Label sumbu Y (kemungkinan)
label_kemungkinan = [
    "A - Sangat Jarang Terjadi",
    "B - Jarang Terjadi",
    "C - Bisa Terjadi",
    "D - Sangat Mungkin Terjadi",
    "E - Hampir Pasti Terjadi",
]

# Label sumbu X (dampak)
label_dampak = [
    "1 Sangat Rendah",
    "2 Rendah",
    "3 Moderat",
    "4 Tinggi",
    "5 Sangat Tinggi",
]

# Teks dalam kotak: hanya angka skala
text_values = []
for i in range(5):
    baris = []
    for j in range(5):
        baris.append(str(matriks_skala[i][j]))
    text_values.append(baris)

fig = go.Figure(data=go.Heatmap(
    z=matriks_skala,
    x=label_dampak,
    y=label_kemungkinan,
    text=text_values,
    texttemplate="%{text}",
    textfont={"size": 12, "color": "black"},
    colorscale=[[0, "#ffffff"], [1, "#ffffff"]],  # netral, warna diatur manual
    showscale=False,
    hoverinfo="text",
    hovertext=[
        [
            f"Kemungkinan: {label_kemungkinan[i]}<br>"
            f"Dampak: {label_dampak[j]}<br>"
            f"Skala: {matriks_skala[i][j]}<br>"
            f"Level: {matriks_level[i][j]}"
            for j in range(5)
        ]
        for i in range(5)
    ],
))

# Tambahkan kotak warna manual
for i in range(5):
    for j in range(5):
        fig.add_shape(
            type="rect",
            x0=j - 0.5, x1=j + 0.5,
            y0=i - 0.5, y1=i + 0.5,
            fillcolor=warna_matriks[i][j],
            line=dict(color="white", width=1),
            layer="below",
        )

# Tambahkan titik posisi kategori aktual
for _, row in prob_df.iterrows():
    fig.add_trace(go.Scatter(
        x=[row["Tingkat Dampak"]],
        y=[row["Kemungkinan"]],
        mode="markers+text",
        marker=dict(
            size=22,
            color="white",
            line=dict(color="black", width=2),
        ),
        text=[row["Kode"]],
        textposition="middle center",
        textfont=dict(color="black", size=11),
        showlegend=False,
        hoverinfo="skip",
    ))

fig.update_layout(
    height=600,
    xaxis_title="Skala Dampak",
    yaxis_title="Skala Kemungkinan",
    margin=dict(l=40, r=40, t=40, b=40),
    plot_bgcolor="white",
)

fig.update_xaxes(
    side="bottom",
    tickfont=dict(size=11),
)

fig.update_yaxes(
    tickfont=dict(size=11),
)

st.plotly_chart(fig, use_container_width=True)

# =========================================================
# LEGENDA WARNA
# =========================================================
st.subheader("Legenda Warna")

st.markdown(
    """
    **Legenda warna berdasarkan 0012.E-2024 Edir Juknis Perencanaan Manajemen Risiko Terintegrasi**
    """
)

legenda_html = """
<div style="display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px;">
    <div style="background-color: #2ecc71; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold;">
        1–5 • Low
    </div>
    <div style="background-color: #a8d08d; color: black; padding: 10px 20px; border-radius: 5px; font-weight: bold;">
        6–10 • Low to Moderate
    </div>
    <div style="background-color: #ffd966; color: black; padding: 10px 20px; border-radius: 5px; font-weight: bold;">
        11–15 • Moderate
    </div>
    <div style="background-color: #f4b183; color: black; padding: 10px 20px; border-radius: 5px; font-weight: bold;">
        16–19 • Moderate to High
    </div>
    <div style="background-color: #e06666; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold;">
        20–25 • High
    </div>
</div>
"""

st.markdown(legenda_html, unsafe_allow_html=True)

# =========================================================
# LEGENDA KODE KATEGORI
# =========================================================
st.subheader("Keterangan Kode Kategori")

kode_legend = prob_df[["Kode", "Kategori", "Tingkat Dampak", "Kemungkinan", "Level Risiko", "Skala Risiko"]]
st.dataframe(kode_legend, use_container_width=True, hide_index=True)

st.divider()

st.info("Fase 4 selesai. Selanjutnya: skenario aktual, target, dan what-if.")
