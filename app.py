import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ==========================================
# 0. KONFIGURASI HALAMAN LEBAR (WIDE MODE)
# ==========================================
st.set_page_config(
    page_title="Dashboard Insentif Fiskal - Princess Edition",
    page_icon="👑",
    layout="wide"
)

# Custom CSS pink princess ceria & full width
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #fff0f5 0%, #ffe4e1 50%, #ffc0cb 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #fff0f5 0%, #ffe4e1 50%, #ffc0cb 100%);
    }
    h1, h2, h3 {
        color: #d1477a !important;
        font-family: 'Quicksand', sans-serif;
    }
    .card-container {
        background: linear-gradient(135deg, #fff5f8 0%, #ffeef2 100%);
        border: 2px dashed #ff69b4;
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 5px 15px rgba(255, 192, 203, 0.4);
        margin-bottom: 20px;
    }
    .card-title {
        font-size: 1rem;
        color: #c71585;
        font-weight: bold;
    }
    .card-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #8b008b;
        margin-top: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. LOAD & BERSIHKAN DATA (DENGAN CACHE TTL 3 MENIT)
# ==========================================
url_simulasi = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTs1RqydMwCiImnExjhqC1B_MlnxJaJO5m0UZXOsPPNSyGbphKBK6Wq0bBqpkmmXvkDUMh_LrUcX-Jy/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=300) # Otomatis refresh data setiap 3 menit (300 detik)
def load_data(url):
    df_raw = pd.read_csv(url, header=None)
    df_simulasi = pd.DataFrame({
        'Jenis': [df_raw.iloc[2, 0], df_raw.iloc[3, 0]],
        '0%': [df_raw.iloc[2, 1], df_raw.iloc[3, 1]],
        '30%': [df_raw.iloc[2, 2], df_raw.iloc[3, 2]],
        '50%': [df_raw.iloc[2, 3], df_raw.iloc[3, 3]],
        '75%': [df_raw.iloc[2, 4], df_raw.iloc[3, 4]],
        'KETERANGAN': [df_raw.iloc[2, 5], df_raw.iloc[3, 5]]
    })
    
    for col in ['0%', '30%', '50%', '75%']:
        df_simulasi[col] = (
            df_simulasi[col]
            .astype(str)
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False)
            .astype(float)
        )
    return df_simulasi

try:
    df_simulasi = load_data(url_simulasi)
except Exception as e:
    df_simulasi = pd.DataFrame()
    st.error(f"Gagal memuat data dari spreadsheet: {e}")

# Tombol Refresh Manual di bagian atas
col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    if st.button("🔄 Segarkan Data"):
        st.cache_data.clear() # Membersihkan cache agar mengambil data terbaru dari Google Sheets
        st.rerun()

# ==========================================
# 2. HEADER & DROPDOWN PILIHAN INSENTIF FISKAL
# ==========================================
st.title("👑 Dashboard Analisa Insentif Fiskal - Princess Edition 💖")
st.markdown("### ✨ Simulasi Matriks Ketetapan & Potensi Realisasi Pendapatan")

if not df_simulasi.empty:
    # Widget Dropdown interaktif
    pilihan_diskon = st.selectbox(
        "🎯 Pilih Besaran Insentif Fiskal untuk Kartu Ringkasan:",
        options=['0%', '30%', '50%', '75%'],
        index=0
    )

    val_ket = df_simulasi.loc[0, pilihan_diskon]
    val_pot = df_simulasi.loc[1, pilihan_diskon]
    selisih = val_ket - val_pot

    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        st.markdown(f"""
            <div class="card-container">
                <div class="card-title">👑 Ketetapan ({pilihan_diskon})</div>
                <div class="card-value">Rp {val_ket/1e9:,.2f} Milyar</div>
            </div>
        """, unsafe_allow_html=True)
    with col_c2:
        st.markdown(f"""
            <div class="card-container">
                <div class="card-title">✨ Potensi Realisasi ({pilihan_diskon})</div>
                <div class="card-value">Rp {val_pot/1e9:,.2f} Milyar</div>
            </div>
        """, unsafe_allow_html=True)
    with col_c3:
        st.markdown(f"""
            <div class="card-container">
                <div class="card-title">🎀 Potensi Selisih / Efisiensi</div>
                <div class="card-value">Rp {selisih/1e9:,.2f} Milyar</div>
            </div>
        """, unsafe_allow_html=True)

    st.write("---")

    # ==========================================
    # 3. TABEL MATRIKS (FULL WIDTH)
    # ==========================================
    st.markdown("📋 **Tabel Matriks Proyeksi Berdasarkan Insentif Fiskal**")
    
    df_tampil = df_simulasi.copy()
    for col in ['0%', '30%', '50%', '75%']:
        df_tampil[col] = df_tampil[col].apply(lambda x: f"Rp {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') if pd.notnull(x) else "-")
            
    st.dataframe(df_tampil, use_container_width=True, hide_index=True)

    st.write("---")

    # ==========================================
    # 4. GRAFIK KURVA
    # ==========================================
    st.markdown("#### 📈 Kurva Perbandingan Ketetapan vs Potensi Realisasi")

    kategori_x = [0, 30, 50, 75]
    
    row_ketetapan = df_simulasi.iloc[0]
    row_potensi = df_simulasi.iloc[1]

    val_ketetapan = [row_ketetapan.get('0%', 0), row_ketetapan.get('30%', 0), row_ketetapan.get('50%', 0), row_ketetapan.get('75%', 0)]
    val_potensi = [row_potensi.get('0%', 0), row_potensi.get('30%', 0), row_potensi.get('50%', 0), row_potensi.get('75%', 0)]
    
    label_ketetapan = str(row_ketetapan.get('Jenis', 'Ketetapan')) + " (" + str(row_ketetapan.get('KETERANGAN', 'Ketetapan saat ini')) + ")"
    label_potensi = str(row_potensi.get('Jenis', 'Potensi Realisasi'))

    fig = go.Figure()

    # 1. Potensi Realisasi (Belakang)
    fig.add_trace(go.Scatter(
        x=kategori_x,
        y=val_potensi,
        mode='lines+markers',
        name=label_potensi,
        fill='tozeroy',
        fillcolor='rgba(230, 126, 34, 0.12)',
        line=dict(shape='spline', color='#E67E22', width=3.5, dash='dash'),
        marker=dict(size=9, color='#E67E22'),
        hovertemplate="<b>Potensi Realisasi (%{x}):</b> Rp %{y:,.2f}<extra></extra>"
    ))

    # 2. Ketetapan (Depan)
    text_labels = [f"Rp {val/1e9:.2f} Milyar" for val in val_ketetapan]
    
    fig.add_trace(go.Scatter(
        x=kategori_x,
        y=val_ketetapan,
        mode='lines+markers+text',
        name=label_ketetapan,
        text=text_labels,
        textposition=["top right", "top center", "top center", "top right"],
        textfont=dict(color='#4A0E4E', size=12, family='Quicksand', weight='bold'),
        fill='tozeroy',
        fillcolor='rgba(199, 21, 133, 0.15)',
        line=dict(shape='spline', color='#C71585', width=4),
        marker=dict(size=10, color='#C71585'),
        hovertemplate="<b>Ketetapan (%{x}):</b> Rp %{y:,.2f}<extra></extra>"
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(255,255,255,0.9)',
        height=540,
        xaxis=dict(
            title='<b>Besaran Insentif Fiskal (%)</b>',
            tickmode='array',
            tickvals=[0, 30, 50, 75],
            ticktext=['0%', '30%', '50%', '75%'],
            showgrid=True,
            gridcolor='rgba(230, 230, 230, 0.6)',
            tickfont=dict(color='#C71585', size=13, weight='bold'),
            range=[-5, 84]
        ),
        yaxis=dict(
            title='<b>Proyeksi Nilai (Rupiah)</b>',
            showgrid=True,
            gridcolor='rgba(230, 230, 230, 0.6)',
            tickfont=dict(color='#C71585', size=12),
            range=[0, 43e9],
            tickformat=',.0f'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(255,255,255,0.9)'
        ),
        hovermode="x unified",
        margin=dict(l=40, r=60, t=50, b=30)
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Data belum termuat.")
