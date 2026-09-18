import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
import plotly.graph_objects as go
from html import escape

# =========================================================
# KONFIGURASI HALAMAN
# =========================================================
st.set_page_config(
    page_title="Risk Modelling Kecelakaan Kerja",
    layout="wide"
)

# =========================================================
# CUSTOM CSS — Tabel HTML
# =========================================================
st.markdown("""
<style>
.table-custom {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
    margin-top: 8px;
    margin-bottom: 8px;
}
.table-custom thead th {
    background-color: #1f4e79;
    color: #ffffff;
    font-weight: bold;
    text-align: center;
    padding: 8px 10px;
    border: 1px solid #d0d0d0;
}
.table-custom tbody td {
    padding: 6px 10px;
    border: 1px solid #e0e0e0;
    text-align: center;
}
.table-custom tbody tr:nth-child(even) {
    background-color: #f5f9ff;
}
.table-custom tbody tr:nth-child(odd) {
    background-color: #ffffff;
}
.table-custom tbody tr:hover {
    background-color: #e6f0ff;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# FUNGSI HELPER — Render tabel HTML statis
# =========================================================
def render_tabel(df, kolom=None, judul=None):
    if kolom is not None:
        df_tampil = df[kolom].copy()
    else:
        df_tampil = df.copy()

    if judul:
        st.markdown(f"**{judul}**")

    html = '<table class="table-custom"><thead><tr>'
    for col in df_tampil.columns:
        html += f'<th>{escape(str(col))}</th>'
    html += '</tr></thead><tbody>'

    for _, row in df_tampil.iterrows():
        html += '<tr>'
        for val in row:
            html += f'<td>{escape(str(val))}</td>'
        html += '</tr>'

    html += '</tbody></table>'
    st.markdown(html, unsafe_allow_html=True)


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
    berdasarkan data historis, dengan pendekatan **semi-kuantitatif**.

    ---

    ### 🧭 Alur Penggunaan

    #### 1. Data Historis Kecelakaan Kerja
    Tabel bersifat **read-only**. Untuk mengedit, klik tombol **"Edit Data"**.

    #### 2. Rata-Rata Kejadian per Tahun (Lambda)
    Dihitung otomatis dari data historis.

    #### 3. Probabilitas Poisson
    Lambda dikonversi menjadi probabilitas kejadian.

    #### 4. Matriks Risiko 5×5
    Probabilitas dipetakan ke matriks untuk menghasilkan
    Level Risiko dan Skala Risiko.

    #### 5. Parameter Mitigasi & Skenario
    Ubah parameter mitigasi, KRI, dan what-if.

    #### 6. Tiga Skenario Risiko
    Perbandingan Actual Risk, Targeted Risk, dan What-If Scenario.

    #### 7. Heatmap Tiga Skenario
    Visualisasi matriks risiko 5×5 dengan tiga penanda.

    ---
    """)

    st.markdown("### 🎨 Legenda Warna")
    st.markdown(
        "Warna heatmap mengikuti **0012.E-2024 Edir Juknis Perencanaan "
        "Manajemen Risiko Terintegrasi**:"
    )

    legenda_panduan = """
    <div style="display:flex; flex-direction:column; gap:0; margin-top:10px;">
      <div style="display:flex; align-items:center;">
        <div style="width:120px; height:32px; background:#4CAF50; border:1px solid #ccc;"></div>
        <div style="padding-left:12px; font-style:italic; font-size:15px;">Low</div>
      </div>
      <div style="display:flex; align-items:center;">
        <div style="width:120px; height:32px; background:#A5D6A7; border:1px solid #ccc;"></div>
        <div style="padding-left:12px; font-style:italic; font-size:15px;">Low to Moderate</div>
      </div>
      <div style="display:flex; align-items:center;">
        <div style="width:120px; height:32px; background:#FFFF00; border:1px solid #ccc;"></div>
        <div style="padding-left:12px; font-style:italic; font-size:15px;">Moderate</div>
      </div>
      <div style="display:flex; align-items:center;">
        <div style="width:120px; height:32px; background:#ED7D31; border:1px solid #ccc;"></div>
        <div style="padding-left:12px; font-style:italic; font-size:15px;">Moderate to High</div>
      </div>
      <div style="display:flex; align-items:center;">
        <div style="width:120px; height:32px; background:#E53935; border:1px solid #ccc;"></div>
        <div style="padding-left:12px; font-style:italic; font-size:15px;">High</div>
      </div>
    </div>
    """
    st.markdown(legenda_panduan, unsafe_allow_html=True)

    st.markdown("""
    ---

    ### 💡 Tips Penggunaan
    1. Pastikan data historis sudah benar.
    2. Perhatikan perubahan Lambda.
    3. Gunakan slider mitigasi.
    4. Bandingkan tiga skenario.
    5. Hover pada heatmap untuk detail.

    ### 📌 Catatan
    - Bersifat **semi-kuantitatif**.
    - Tidak menggantikan penilaian ahli.

    ### 🚀 Mulai
    Silakan pindah ke tab **📊 Dashboard**.
    """)

# =========================================================
# TAB 2 — DASHBOARD
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

    if "data_historis" not in st.session_state:
        st.session_state["data_historis"] = default_data.copy()

    if "mode_edit" not in st.session_state:
        st.session_state["mode_edit"] = False

    col_btn1, col_btn2 = st.columns([1, 5])
    with col_btn1:
        if not st.session_state["mode_edit"]:
            if st.button("✏️ Edit Data"):
                st.session_state["mode_edit"] = True
                st.rerun()
        else:
            if st.button("✅ Selesai Edit"):
                st.session_state["mode_edit"] = False
                st.rerun()

    if st.session_state["mode_edit"]:
        edited_data = st.data_editor(
            st.session_state["data_historis"],
            num_rows="dynamic",
            use_container_width=True,
            key="editor_data_historis",
        )
        st.session_state["data_historis"] = edited_data
    else:
        render_tabel(st.session_state["data_historis"])

    edited_data = st.session_state["data_historis"]

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
            round(edited_data["Tidak Ada Korban"].mean(), 4),
            round(edited_data["Luka Ringan"].mean(), 4),
            round(edited_data["Luka Berat"].mean(), 4),
            round(edited_data["Cacat Permanen"].mean(), 4),
            round(edited_data["Fatality"].mean(), 4),
        ],
    })

    render_tabel(lambda_df)
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
        lambda r: round(hitung_probabilitas(r["Lambda"], r["Dampak Atas"], r["Dampak Bawah"]), 4),
        axis=1
    )

    render_tabel(prob_df, kolom=["Kode", "Kategori", "Lambda", "Probabilitas"])

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

    render_tabel(prob_df, kolom=[
        "Kode", "Kategori", "Tingkat Dampak",
        "Probabilitas", "Kemungkinan",
        "Level Risiko", "Skala Risiko"
    ])
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

    render_tabel(output_df)
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

    render_tabel(skenario_df, kolom=[
        "Kode", "Kategori", "Tingkat Dampak", "Lambda",
        "Actual Risk", "Targeted Risk", "What-If Scenario",
        "Kemungkinan Actual Risk", "Level Actual Risk", "Skala Actual Risk",
        "Kemungkinan Targeted Risk", "Level Targeted Risk", "Skala Targeted Risk",
        "Kemungkinan What-If Scenario", "Level What-If Scenario", "Skala What-If Scenario",
    ])
    st.divider()

    # =========================================================
    # FASE 5C — HEATMAP TIGA SKENARIO
    # =========================================================
    st.header("7. Heatmap Tiga Skenario")

    label_dampak = [
        "1 Sangat Rendah",
        "2 Rendah",
        "3 Moderat",
        "4 Tinggi",
        "5 Sangat Tinggi",
    ]

    label_kemungkinan = [
        "A - Sangat Jarang",
        "B - Jarang",
        "C - Bisa",
        "D - Sangat Mungkin",
        "E - Hampir Pasti",
    ]

    map_dampak = dict(zip(urutan_dampak, label_dampak))
    map_kemungkinan = dict(zip(urutan_kemungkinan, label_kemungkinan))

    text_values = []
    for i in range(5):
        baris = []
        for j in range(5):
            baris.append(f"{matriks_skala[i][j]}<br>{matriks_level[i][j]}")
        text_values.append(baris)

    # Warna diskrit: Low, Low to Moderate, Moderate, Moderate to High, High (MERAH)
    colorscale = [
        [0.00, "#4CAF50"], [0.20, "#4CAF50"],   # 1-5 Low
        [0.20, "#A5D6A7"], [0.40, "#A5D6A7"],   # 6-10 Low to Moderate
        [0.40, "#FFFF00"], [0.60, "#FFFF00"],   # 11-15 Moderate
        [0.60, "#ED7D31"], [0.76, "#ED7D31"],   # 16-19 Moderate to High
        [0.76, "#E53935"], [1.00, "#E53935"],   # 20-25 High (MERAH)
    ]

    fig = go.Figure()

    fig.add_trace(go.Heatmap(
        z=matriks_skala,
        x=label_dampak,
        y=label_kemungkinan,
        text=text_values,
        texttemplate="%{text}",
        textfont={"size": 11, "color": "black"},
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
                textfont=dict(color="black", size=9),
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
        height=550,
        xaxis_title="Skala Dampak",
        yaxis_title="Skala Kemungkinan",
        margin=dict(l=120, r=40, t=20, b=60),
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
    <div style="display:flex; flex-direction:column; gap:0; margin-top:8px;">
      <div style="display:flex; align-items:center;">
        <div style="width:120px; height:32px; background:#4CAF50; border:1px solid #ccc;"></div>
        <div style="padding-left:12px; font-style:italic; font-size:15px;">Low</div>
      </div>
      <div style="display:flex; align-items:center;">
        <div style="width:120px; height:32px; background:#A5D6A7; border:1px solid #ccc;"></div>
        <div style="padding-left:12px; font-style:italic; font-size:15px;">Low to Moderate</div>
      </div>
      <div style="display:flex; align-items:center;">
        <div style="width:120px; height:32px; background:#FFFF00; border:1px solid #ccc;"></div>
        <div style="padding-left:12px; font-style:italic; font-size:15px;">Moderate</div>
      </div>
      <div style="display:flex; align-items:center;">
        <div style="width:120px; height:32px; background:#ED7D31; border:1px solid #ccc;"></div>
        <div style="padding-left:12px; font-style:italic; font-size:15px;">Moderate to High</div>
      </div>
      <div style="display:flex; align-items:center;">
        <div style="width:120px; height:32px; background:#E53935; border:1px solid #ccc;"></div>
        <div style="padding-left:12px; font-style:italic; font-size:15px;">High</div>
      </div>
    </div>
    """
    st.markdown(legenda_html, unsafe_allow_html=True)

    st.divider()
    st.info("Fase 5 selesai. Selanjutnya: validasi dan rekomendasi otomatis.")
