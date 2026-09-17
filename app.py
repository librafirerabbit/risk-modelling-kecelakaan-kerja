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
    prob_df[["Kode", "Kategori", "Lambda", "Probabilitas"]],
    use_container_width=True,
    hide_index=True
)

st.bar_chart(prob_df.set_index("Kategori")["Probabilitas"], use_container_width=True)

st.divider()

# =========================================================
# FASE 3 — MATRIKS RISIKO
# =========================================================
st.header("4. Matriks Risiko 5x5")

def kategori_kemungkinan(p):
    if p < 0.2: return "Sangat Jarang Terjadi"
    elif p < 0.4: return "Jarang Terjadi"
    elif p < 0.6: return "Bisa Terjadi"
    elif p < 0.8: return "Sangat Mungkin Terjadi"
    else: return "Hampir Pasti Terjadi"

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

def level_risiko(k, d):
    return matriks_level[urutan_kemungkinan.index(k)][urutan_dampak.index(d)]

def skala_risiko(k, d):
    return matriks_skala[urutan_kemungkinan.index(k)][urutan_dampak.index(d)]

prob_df["Level Risiko"] = prob_df.apply(
    lambda r: level_risiko(r["Kemungkinan"], r["Tingkat Dampak"]), axis=1
)
prob_df["Skala Risiko"] = prob_df.apply(
    lambda r: skala_risiko(r["Kemungkinan"], r["Tingkat Dampak"]), axis=1
)

st.dataframe(
    prob_df[[
        "Kode", "Kategori", "Tingkat Dampak",
        "Probabilitas", "Kemungkinan",
        "Level Risiko", "Skala Risiko"
    ]],
    use_container_width=True,
    hide_index=True
)

st.divider()

# =========================================================
# FASE 4 — HEATMAP (VERSI PERBAIKAN)
# =========================================================
st.header("5. Heatmap Matriks Risiko")

# Warna diskrit berdasarkan skala risiko
def warna_skala(n):
    if 1 <= n <= 5:   return "#2ecc71"
    elif 6 <= n <= 10: return "#a8d08d"
    elif 11 <= n <= 15: return "#ffd966"
    elif 16 <= n <= 19: return "#f4b183"
    else: return "#e06666"

# Label sumbu
label_dampak = ["1 Sangat Rendah", "2 Rendah", "3 Moderat", "4 Tinggi", "5 Sangat Tinggi"]
label_kemungkinan = [
    "A - Sangat Jarang",
    "B - Jarang",
    "C - Bisa",
    "D - Sangat Mungkin",
    "E - Hampir Pasti",
]

# Teks angka di dalam kotak
text_values = [[str(matriks_skala[i][j]) for j in range(5)] for i in range(5)]

fig = go.Figure()

# Heatmap dasar (pakai colorscale diskrit)
# Nilai 1-25 dipetakan ke 5 blok warna
colorscale = [
    [0.00, "#2ecc71"], [0.20, "#2ecc71"],   # 1-5
    [0.20, "#a8d08d"], [0.40, "#a8d08d"],   # 6-10
    [0.40, "#ffd966"], [0.60, "#ffd966"],   # 11-15
    [0.60, "#f4b183"], [0.76, "#f4b183"],   # 16-19
    [0.76, "#e06666"], [1.00, "#e06666"],   # 20-25
]

fig.add_trace(go.Heatmap(
    z=matriks_skala,
    x=label_dampak,
    y=label_kemungkinan,
    text=text_values,
    texttemplate="%{text}",
    textfont={"size": 13, "color": "black"},
    colorscale=colorscale,
    zmin=1, zmax=25,
    showscale=False,
    hoverinfo="skip",
    xgap=2, ygap=2,
))

# Titik kategori aktual
for _, row in prob_df.iterrows():
    fig.add_trace(go.Scatter(
        x=[row["Tingkat Dampak"]],
        y=[row["Kemungkinan"]],
        mode="markers+text",
        marker=dict(size=28, color="white",
                    line=dict(color="black", width=2)),
        text=[row["Kode"]],
        textposition="middle center",
        textfont=dict(color="black", size=11),
        showlegend=False,
        hovertemplate=(
            f"<b>{row['Kode']} - {row['Kategori']}</b><br>"
            f"Kemungkinan: {row['Kemungkinan']}<br>"
            f"Dampak: {row['Tingkat Dampak']}<br>"
            f"Skala: {row['Skala Risiko']}<br>"
            f"Level: {row['Level Risiko']}<extra></extra>"
        ),
    ))

fig.update_layout(
    height=500,
    xaxis_title="Skala Dampak",
    yaxis_title="Skala Kemungkinan",
    margin=dict(l=80, r=40, t=20, b=60),
    plot_bgcolor="white",
    xaxis=dict(side="bottom", tickfont=dict(size=11)),
    yaxis=dict(tickfont=dict(size=11), autorange="reversed"),
)

st.plotly_chart(fig, use_container_width=True)

# Legenda warna
st.markdown("**Legenda Warna (0012.E-2024 Edir Juknis Perencanaan Manajemen Risiko Terintegrasi)**")

legenda_html = """
<div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:8px;">
  <div style="background:#2ecc71;color:white;padding:8px 16px;border-radius:5px;font-weight:bold;">1–5 • Low</div>
  <div style="background:#a8d08d;color:black;padding:8px 16px;border-radius:5px;font-weight:bold;">6–10 • Low to Moderate</div>
  <div style="background:#ffd966;color:black;padding:8px 16px;border-radius:5px;font-weight:bold;">11–15 • Moderate</div>
  <div style="background:#f4b183;color:black;padding:8px 16px;border-radius:5px;font-weight:bold;">16–19 • Moderate to High</div>
  <div style="background:#e06666;color:white;padding:8px 16px;border-radius:5px;font-weight:bold;">20–25 • High</div>
</div>
"""
st.markdown(legenda_html, unsafe_allow_html=True)

# Keterangan kode
st.markdown("**Keterangan Kode Kategori**")
st.dataframe(
    prob_df[["Kode", "Kategori", "Tingkat Dampak", "Kemungkinan", "Level Risiko", "Skala Risiko"]],
    use_container_width=True, hide_index=True
)

st.divider()
st.info("Fase 4 selesai. Selanjutnya: skenario aktual, target, dan what-if.")
