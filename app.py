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

# =========================================================
# TAB UTAMA
# =========================================================
tab_panduan, tab_dashboard = st.tabs(["📖 Panduan", "📊 Dashboard"])

# =========================================================
# TAB 1 — PANDUAN
# =========================================================
with tab_panduan:
    st.header("Panduan Penggunaan Aplikasi")

    st.markdown("""
    Selamat datang di **Dashboard Risk Modelling Kecelakaan Kerja**.

    Aplikasi ini digunakan untuk memodelkan risiko kecelakaan kerja
    berdasarkan data historis, dengan pendekatan **semi-kuantitatif**
    yang menggabungkan:

    - Distribusi **Poisson** untuk menghitung probabilitas kejadian.
    - **Matriks Risiko 5×5** untuk menentukan level risiko.
    - **Faktor Koreksi KRI** dan **Mitigasi** untuk menyesuaikan risiko.
    - **Tiga skenario** perbandingan: Aktual, Target, dan What-If.

    ---

    ### 🧭 Alur Penggunaan

    Aplikasi ini terdiri dari **7 bagian utama** di tab **Dashboard**.
    Ikuti urutannya dari atas ke bawah.

    #### 1. Data Historis Kecelakaan Kerja
    Di bagian ini, kamu melihat tabel data kecelakaan kerja
    dari tahun ke tahun, dengan kolom:

    - Tahun
    - Tidak Ada Korban
    - Luka Ringan
    - Luka Berat
    - Cacat Permanen
    - Fatality

    **Tabel ini bisa diedit langsung.**  
    Klik angka di dalam sel, ubah sesuai data terbaru, dan
    perubahan akan langsung dipakai untuk perhitungan di bawahnya.

    #### 2. Rata-Rata Kejadian per Tahun (Lambda)
    Bagian ini menampilkan **nilai Lambda** untuk tiap kategori dampak.
    Lambda dihitung otomatis dari rata-rata kolom di bagian 1.

    Lambda inilah yang menjadi **dasar distribusi Poisson** di bagian
    berikutnya.

    #### 3. Probabilitas Poisson
    Di sini, nilai Lambda dikonversi menjadi **probabilitas kejadian**
    menggunakan distribusi Poisson.

    Probabilitas ini menjawab pertanyaan:

    > "Berapa peluang terjadinya sejumlah kecelakaan dalam satu tahun?"

    Hasilnya ditampilkan dalam tabel dan grafik batang.

    #### 4. Matriks Risiko 5×5
    Probabilitas tadi dikonversi menjadi **kategori kemungkinan**:

    - Sangat Jarang Terjadi
    - Jarang Terjadi
    - Bisa Terjadi
    - Sangat Mungkin Terjadi
    - Hampir Pasti Terjadi

    Lalu dipetakan ke **matriks risiko 5×5** bersama tingkat dampak,
    menghasilkan:

    - **Level Risiko** (Low, Low to Moderate, Moderate, dst.)
    - **Skala Risiko** (1–25)

    #### 5. Parameter Mitigasi & Skenario
    Di bagian ini, kamu bisa **mengubah parameter**:

    - Efek Workshop K3
    - Efek Sertifikasi K3
    - Efek Pelaksanaan FRA
    - Kontribusi KRI 1, 2, 3
    - Nilai What-If Skenario

    Semua parameter di atas **read-write** (bisa diubah).  
    Setelah diubah, **output otomatis** akan muncul:

    - Faktor Koreksi tiap mitigasi
    - Total Faktor Mitigasi
    - Faktor Eskalasi KRI

    #### 6. Tiga Skenario Risiko
    Bagian ini menampilkan **satu tabel gabungan** dengan kolom pembanding:

    - **Actual Risk** → risiko berdasarkan data historis
    - **Targeted Risk** → risiko setelah mitigasi
    - **What-If Scenario** → risiko jika skenario tertentu terjadi

    Untuk masing-masing skenario, ditampilkan juga:

    - Probabilitas
    - Kemungkinan
    - Level Risiko
    - Skala Risiko

    #### 7. Heatmap Tiga Skenario
    Visualisasi akhir: **heatmap matriks risiko 5×5** dengan tiga
    penanda:

    - **K1, K2, ...** → Actual Risk (border hitam)
    - **K1', K2', ...** → Targeted Risk (border biru)
    - **K1", K2", ...** → What-If Scenario (border merah)

    Arahkan kursor ke titik untuk melihat detail.

    ---

    ### 🎨 Legenda Warna

    Warna heatmap mengikuti **0012.E-2024 Edir Juknis Perencanaan
    Manajemen Risiko Terintegrasi**:

    - 🟩 **1–5** → Low
    - 🟨 **6–10** → Low to Moderate
    - 🟧 **11–15** → Moderate
    - 🟥 **16–19** → Moderate to High
    - 🟪 **20–25** → High

    ---

    ### 💡 Tips Penggunaan

    1. **Mulai dari data historis.**  
       Pastikan data di bagian 1 sudah benar sebelum melihat hasil.

    2. **Perhatikan perubahan Lambda.**  
       Kalau data historis berubah, Lambda ikut berubah, dan
       seluruh perhitungan di bawahnya juga berubah.

    3. **Gunakan slider mitigasi.**  
       Coba ubah nilai mitigasi untuk melihat dampaknya ke
       Targeted Risk dan What-If Scenario.

    4. **Bandingkan tiga skenario.**  
       Gunakan tabel di bagian 6 untuk membandingkan posisi risiko
       aktual, target, dan what-if.

    5. **Hover pada heatmap.**  
       Untuk melihat detail tiap titik tanpa harus membaca tabel.

    ---

    ### 📌 Catatan

    - Aplikasi ini bersifat **semi-kuantitatif**.  
      Artinya, hasilnya bergantung pada asumsi parameter yang
      dimasukkan, bukan prediksi presisi tinggi.

    - Data historis yang lebih panjang dan lengkap akan
      menghasilkan model yang lebih stabil.

    - Aplikasi ini **tidak menggantikan penilaian ahli** (expert
      judgement) dalam pengambilan keputusan risiko.

    ---

    ### 🚀 Mulai

    Silakan pindah ke tab **📊 Dashboard** untuk mulai menggunakan
    aplikasi.
    """)

# =========================================================
# TAB 2 — DASHBOARD (FASE 1 s/d 5)
# =========================================================
with tab_dashboard:

    st.divider()

    # =========================================================
    # FASE 1 — DATA HISTORIS
    # =========================================================
    st.header("1. Data Historis Kecelakaan Kerja")

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
            "Tidak Ada Korban", "Luka Ringan", "Luka Berat",
            "Cacat Permanen", "Fatality",
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
        "Kategori": ["Tidak Ada Korban", "Luka Ringan", "Luka Berat", "Cacat Permanen", "Fatality"],
        "Tingkat Dampak": ["Sangat Rendah", "Rendah", "Moderat", "Tinggi", "Sangat Tinggi"],
        "Dampak Atas": [5, 5, 5, 5, 2],
        "Dampak Bawah": [1, 1, 1, 1, 1],
    })

    prob_df = konfigurasi.merge(lambda_df, on="Kategori")

    def hitung_probabilitas(lam, atas, bawah):
        if lam <= 0:
            return 0.0
        return poisson.cdf(atas, lam) - poisson.cdf(bawah - 1, lam)

    prob_df["Probabilitas"] = prob_df.apply(
        lambda r: hitung_probabilitas(r["Lambda"], r["Dampak Atas"], r["Dampak Bawah"]),
        axis=1
    )
    prob_df["Probabilitas"] = prob_df["Probabilitas"].round(4)

    st.dataframe(
        prob_df[["Kode", "Kategori", "Lambda", "Probabilitas"]],
        use_container_width=True, hide_index=True
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
        "Sangat Jarang Terjadi", "Jarang Terjadi", "Bisa Terjadi",
        "Sangat Mungkin Terjadi", "Hampir Pasti Terjadi",
    ]
    urutan_dampak = [
        "Sangat Rendah", "Rendah", "Moderat", "Tinggi", "Sangat Tinggi",
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
        use_container_width=True, hide_index=True
    )
    st.divider()

    # =========================================================
    # FASE 5 — INPUT MANUAL & OUTPUT OTOMATIS
    # =========================================================
    st.header("5. Parameter Mitigasi & Skenario")

    col_in1, col_in2 = st.columns(2)

    with col_in1:
        st.subheader("Input Mitigasi")
        efek_workshop = st.number_input(
            "Efek Workshop K3", min_value=0.0, max_value=1.0,
            value=0.2, step=0.01, key="efek_workshop"
        )
        efek_sertifikasi = st.number_input(
            "Efek Sertifikasi K3", min_value=0.0, max_value=1.0,
            value=0.2, step=0.01, key="efek_sertifikasi"
        )
        efek_fra = st.number_input(
            "Efek Pelaksanaan FRA", min_value=0.0, max_value=1.0,
            value=0.2, step=0.01, key="efek_fra"
        )

    with col_in2:
        st.subheader("Input KRI & What-If")
        kri1 = st.number_input(
            "Kontribusi KRI 1 (Patrol K3)", min_value=0.0, max_value=1.0,
            value=0.02, step=0.01, key="kri1"
        )
        kri2 = st.number_input(
            "Kontribusi KRI 2 (FPS Unit)", min_value=0.0, max_value=1.0,
            value=0.04, step=0.01, key="kri2"
        )
        kri3 = st.number_input(
            "Kontribusi KRI 3 (Leadership)", min_value=0.0, max_value=1.0,
            value=0.02, step=0.01, key="kri3"
        )
        what_if_nilai = st.number_input(
            "Nilai What If Skenario", min_value=0.0,
            value=5.0, step=0.5, key="what_if"
        )

    st.subheader("Output Otomatis")

    faktor_kri1 = 1 + kri1
    faktor_kri2 = 1 + kri2
    faktor_kri3 = 1 + kri3
    faktor_eskalasi = faktor_kri1 * faktor_kri2 * faktor_kri3

    faktor_koreksi_workshop = 1 - efek_workshop
    faktor_koreksi_sertifikasi = 1 - efek_sertifikasi
    faktor_koreksi_fra = 1 - efek_fra
    total_faktor_mitigasi = (
        faktor_koreksi_workshop *
        faktor_koreksi_sertifikasi *
        faktor_koreksi_fra
    )

    output_df = pd.DataFrame({
        "Parameter": [
            "Faktor KRI 1", "Faktor KRI 2", "Faktor KRI 3",
            "Faktor Eskalasi KRI",
            "Faktor Koreksi Workshop", "Faktor Koreksi Sertifikasi",
            "Faktor Koreksi FRA", "Total Faktor Mitigasi",
        ],
        "Nilai": [
            round(faktor_kri1, 4),
            round(faktor_kri2, 4),
            round(faktor_kri3, 4),
            round(faktor_eskalasi, 4),
            round(faktor_koreksi_workshop, 4),
            round(faktor_koreksi_sertifikasi, 4),
            round(faktor_koreksi_fra, 4),
            round(total_faktor_mitigasi, 4),
        ],
    })

    st.dataframe(output_df, use_container_width=True, hide_index=True)
    st.divider()

    # =========================================================
    # FASE 5B — TIGA SKENARIO
    # =========================================================
    st.header("6. Tiga Skenario Risiko")

    skenario_df = prob_df.copy()

    skenario_df["Actual Risk"] = (
        skenario_df["Lambda"] * faktor_eskalasi
    ).round(4)

    skenario_df["Targeted Risk"] = (
        skenario_df["Actual Risk"] * total_faktor_mitigasi
    ).round(4)

    skenario_df["What-If Scenario"] = (
        skenario_df["Targeted Risk"] + what_if_nilai
    ).round(4)

    def hitung_prob_per_baris(lam, atas, bawah):
        if lam <= 0:
            return 0.0
        return poisson.cdf(atas, lam) - poisson.cdf(bawah - 1, lam)

    for skenario in ["Actual Risk", "Targeted Risk", "What-If Scenario"]:
        prob_col = f"Prob {skenario}"
        kem_col = f"Kemungkinan {skenario}"
        lvl_col = f"Level {skenario}"
        skala_col = f"Skala {skenario}"

        skenario_df[prob_col] = skenario_df.apply(
            lambda r: round(hitung_prob_per_baris(
                r[skenario], r["Dampak Atas"], r["Dampak Bawah"]
            ), 4),
            axis=1
        )
        skenario_df[kem_col] = skenario_df[prob_col].apply(kategori_kemungkinan)
        skenario_df[lvl_col] = skenario_df.apply(
            lambda r: level_risiko(r[kem_col], r["Tingkat Dampak"]), axis=1
        )
        skenario_df[skala_col] = skenario_df.apply(
            lambda r: skala_risiko(r[kem_col], r["Tingkat Dampak"]), axis=1
        )

    tabel_gabungan = skenario_df[[
        "Kode", "Kategori", "Tingkat Dampak", "Lambda",
        "Actual Risk", "Targeted Risk", "What-If Scenario",
        "Kemungkinan Actual Risk", "Level Actual Risk", "Skala Actual Risk",
        "Kemungkinan Targeted Risk", "Level Targeted Risk", "Skala Targeted Risk",
        "Kemungkinan What-If Scenario", "Level What-If Scenario", "Skala What-If Scenario",
    ]]

    st.dataframe(tabel_gabungan, use_container_width=True, hide_index=True)
    st.divider()

    # =========================================================
    # FASE 5C — HEATMAP TIGA SKENARIO
    # =========================================================
    st.header("7. Heatmap Tiga Skenario")

    label_dampak = [
        "1 Sangat Rendah", "2 Rendah", "3 Moderat", "4 Tinggi", "5 Sangat Tinggi"
    ]
    label_kemungkinan = [
        "A - Sangat Jarang", "B - Jarang", "C - Bisa",
        "D - Sangat Mungkin", "E - Hampir Pasti",
    ]

    map_dampak = dict(zip(urutan_dampak, label_dampak))
    map_kemungkinan = dict(zip(urutan_kemungkinan, label_kemungkinan))

    text_values = [[str(matriks_skala[i][j]) for j in range(5)] for i in range(5)]

    colorscale = [
        [0.00, "#2ecc71"], [0.20, "#2ecc71"],
        [0.20, "#a8d08d"], [0.40, "#a8d08d"],
        [0.40, "#ffd966"], [0.60, "#ffd966"],
        [0.60, "#f4b183"], [0.76, "#f4b183"],
        [0.76, "#e06666"], [1.00, "#e06666"],
    ]

    fig = go.Figure()

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

    def tambah_scatter(df, kolom_kemungkinan, kolom_skala, suffix, border_color):
        for _, row in df.iterrows():
            fig.add_trace(go.Scatter(
                x=[map_dampak[row["Tingkat Dampak"]]],
                y=[map_kemungkinan[row[kolom_kemungkinan]]],
                mode="markers+text",
                marker=dict(
                    size=30,
                    color="white",
                    line=dict(color=border_color, width=2),
                ),
                text=[f"{row['Kode']}{suffix}"],
                textposition="middle center",
                textfont=dict(color="black", size=10),
                showlegend=False,
                hovertemplate=(
                    f"<b>{row['Kode']}{suffix} - {row['Kategori']}</b><br>"
                    f"Kemungkinan: {row[kolom_kemungkinan]}<br>"
                    f"Dampak: {row['Tingkat Dampak']}<br>"
                    f"Skala: {row[kolom_skala]}<extra></extra>"
                ),
            ))

    tambah_scatter(skenario_df, "Kemungkinan Actual Risk", "Skala Actual Risk", "", "black")
    tambah_scatter(skenario_df, "Kemungkinan Targeted Risk", "Skala Targeted Risk", "'", "blue")
    tambah_scatter(skenario_df, "Kemungkinan What-If Scenario", "Skala What-If Scenario", '"', "red")

    fig.update_layout(
        height=500,
        xaxis_title="Skala Dampak",
        yaxis_title="Skala Kemungkinan",
        margin=dict(l=100, r=40, t=20, b=60),
        plot_bgcolor="white",
        xaxis=dict(
            side="bottom",
            tickfont=dict(size=11),
            categoryorder="array",
            categoryarray=label_dampak,
        ),
        yaxis=dict(
            tickfont=dict(size=11),
            categoryorder="array",
            categoryarray=label_kemungkinan,
            autorange="reversed",
        ),
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Keterangan Penanda Skenario**")
    st.markdown("""
    - **K1, K2, K3, K4, K5** → Actual Risk (border hitam)
    - **K1', K2', K3', K4', K5'** → Targeted Risk (border biru)
    - **K1", K2", K3", K4", K5"** → What-If Scenario (border merah)
    """)

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

    st.divider()
    st.info("Fase 5 selesai. Selanjutnya: validasi dan rekomendasi otomatis.")
