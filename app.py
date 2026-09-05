import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ==========================================
# 1. LOAD & BERSIHKAN DATA DARI URL GOOGLE SHEETS
# ==========================================
url_simulasi = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTs1RqydMwCiImnExjhqC1B_MlnxJaJO5m0UZXOsPPNSyGbphKBK6Wq0bBqpkmmXvkDUMh_LrUcX-Jy/pub?gid=0&single=true&output=csv"

try:
    df_raw = pd.read_csv(url_simulasi, header=None)
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
except Exception as e:
    df_simulasi = pd.DataFrame()
    st.error(f"Gagal memuat data dari spreadsheet: {e}")

# ==========================================
# 2. VISUALISASI KURVA DENGAN POSISI TEKS AMAN
# ==========================================
st.markdown("### 👑 Kurva Ketetapan vs Potensi Realisasi Insentif Fiskal")

if not df_simulasi.empty:
    st.markdown("📋 **Tabel Matriks Proyeksi Berdasarkan Insentif Fiskal**")
    
    df_tampil = df_simulasi.copy()
    for col in ['0%', '30%', '50%', '75%']:
        df_tampil[col] = df_tampil[col].apply(lambda x: f"Rp {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') if pd.notnull(x) else "-")
            
    st.dataframe(df_tampil, use_container_width=True)

    kategori_x = [0, 30, 50, 75]
    
    row_ketetapan = df_simulasi.iloc[0] if len(df_simulasi) > 0 else None
    row_potensi = df_simulasi.iloc[1] if len(df_simulasi) > 1 else None

    if row_ketetapan is not None and row_potensi is not None:
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
            fillcolor='rgba(230, 126, 34, 0.1)',
            line=dict(shape='spline', color='#E67E22', width=3, dash='dash'),
            marker=dict(size=8, color='#E67E22'),
            hovertemplate="<b>Potensi Realisasi (%{x}):</b> Rp %{y:,.2f}<extra></extra>"
        ))

        # 2. Ketetapan (Depan dengan posisi teks dinamis agar tidak kepotong di ujung)
        text_labels = [f"Rp {val/1e9:.2f}B" for val in val_ketetapan]
        
        fig.add_trace(go.Scatter(
            x=kategori_x,
            y=val_ketetapan,
            mode='lines+markers+text',
            name=label_ketetapan,
            text=text_labels,
            # Mengatur posisi teks per titik: [0% di kanan-atas, 30% di atas, 50% di atas, 75% di kiri-atas]
            textposition=["top right", "top center", "top center", "top left"],
            textfont=dict(color='#C71585', size=11, family='Quicksand', weight='bold'),
            fill='tozeroy',
            fillcolor='rgba(199, 21, 133, 0.15)',
            line=dict(shape='spline', color='#C71585', width=3.5),
            marker=dict(size=9, color='#C71585'),
            hovertemplate="<b>Ketetapan (%{x}):</b> Rp %{y:,.2f}<extra></extra>"
        ))

        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(255,255,255,1)',
            xaxis=dict(
                title='<b>Besaran Insentif Fiskal (%)</b>',
                tickmode='array',
                tickvals=[0, 30, 50, 75],
                ticktext=['0%', '30%', '50%', '75%'],
                showgrid=True,
                gridcolor='rgba(230, 230, 230, 0.5)',
                tickfont=dict(color='#C71585', size=12, weight='bold'),
                range=[-3, 78] # Memberikan sedikit ruang ekstra di kiri dan kanan sumbu X agar teks ujung tidak menempel dinding
            ),
            yaxis=dict(
                title='<b>Proyeksi Nilai (Rp)</b>',
                showgrid=True,
                gridcolor='rgba(230, 230, 230, 0.5)',
                tickfont=dict(color='#C71585', size=11),
                range=[0, 41e9] # Memperluas sedikit batas atas sumbu Y agar teks 0% (37.23B) tidak mentok di atas
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor='rgba(255,255,255,0.8)'
            ),
            hovermode="x unified",
            margin=dict(l=30, r=40, t=40, b=20)
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Struktur baris pada Google Sheet kurang dari 2 baris.")
else:
    st.info("Data belum termuat.")
