import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ==========================================
# 1. LOAD & BERSIHKAN DATA DARI URL GOOGLE SHEETS
# ==========================================
url_simulasi = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTs1RqydMwCiImnExjhqC1B_MlnxJaJO5m0UZXOsPPNSyGbphKBK6Wq0bBqpkmmXvkDUMh_LrUcX-Jy/pub?gid=0&single=true&output=csv"

try:
    df_raw = pd.read_csv(url_simulasi, header=None)
    
    df_simulasi = pd.DataFrame({
        'Jumlah Ketetapan': [df_raw.iloc[2, 0], df_raw.iloc[3, 0]],
        '0%': [df_raw.iloc[2, 1], df_raw.iloc[3, 1]],
        '30%': [df_raw.iloc[2, 2], df_raw.iloc[3, 2]],
        '50%': [df_raw.iloc[2, 3], df_raw.iloc[3, 3]],
        '75%': [df_raw.iloc[2, 4], df_raw.iloc[3, 4]],
        'KETERANGAN': [df_raw.iloc[2, 5], df_raw.iloc[3, 5]]
    })
    
    cols_to_clean = ['0%', '30%', '50%', '75%']
    for col in cols_to_clean:
        df_simulasi[col] = (
            df_simulasi[col]
            .astype(str)
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False)
            .astype(float)
        )
except Exception as e:
    df_simulasi = pd.DataFrame()
    st.error(f"Gagal memuat atau memproses data dari spreadsheet: {e}")

# ==========================================
# 4. SIMULASI & ANALISIS KURVA PARABOLA HALUS
# ==========================================
st.write("---")
st.subheader("👑 Simulasi Kurva Parabola Proyeksi & Potensi Insentif Fiskal")

if not df_simulasi.empty:
    st.markdown("📋 **Tabel Matriks Proyeksi Berdasarkan Insentif Fiskal**")
    
    df_tampil = df_simulasi.copy()
    for col in ['0%', '30%', '50%', '75%']:
        df_tampil[col] = df_tampil[col].apply(lambda x: f"Rp {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') if pd.notnull(x) else "-")
            
    st.dataframe(df_tampil, use_container_width=True)

    st.write("#### 📈 Kurva Parabola Halus (Gap Sumbu X: 0, 10, 20, 30... 75)")

    row_saat_ini = df_simulasi.iloc[0] if len(df_simulasi) > 0 else None
    row_potensi = df_simulasi.iloc[1] if len(df_simulasi) > 1 else None

    if row_saat_ini is not None and row_potensi is not None:
        # Titik data asli
        x_asli = np.array([0, 30, 50, 75])
        
        y_saat_ini_asli = np.array([row_saat_ini.get('0%', 0), row_saat_ini.get('30%', 0), row_saat_ini.get('50%', 0), row_saat_ini.get('75%', 0)])
        y_potensi_asli = np.array([row_potensi.get('0%', 0), row_potensi.get('30%', 0), row_potensi.get('50%', 0), row_potensi.get('75%', 0)])

        # Membuat fitting kurva parabola halus (Polynomial Degree 2)
        poly_saat_ini = np.polyfit(x_asli, y_saat_ini_asli, 2)
        poly_potensi = np.polyfit(x_asli, y_potensi_asli, 2)

        # Rentang sumbu X halus dengan gap per 5 atau 10 (0 sampai 75)
        x_halus = np.linspace(0, 75, 76)
        y_halus_saat_ini = np.polyval(poly_saat_ini, x_halus)
        y_halus_potensi = np.polyval(poly_potensi, x_halus)

        label_bar1 = str(row_saat_ini.get('Jumlah Ketetapan', '1186')) + " (" + str(row_saat_ini.get('KETERANGAN', 'Ketetapan saat ini')) + ")"
        label_bar2 = str(row_potensi.get('Jumlah Ketetapan', '1268')) + " (" + str(row_potensi.get('KETERANGAN', 'Potensi')) + ")"

        fig_sim = go.Figure()

        # 1. Kurva Parabola Bayangan / Potensi di belakang
        fig_sim.add_trace(go.Scatter(
            x=x_halus,
            y=y_halus_potensi,
            mode='lines',
            name=label_bar2,
            line=dict(color='#FF1493', width=3, dash='dash'),
            hovertemplate="<b>Potensi:</b> Rp %{y:,.2f}<extra></extra>"
        ))

        # 2. Kurva Parabola Utama (Saat Ini) dengan isi area bawah transparan
        fig_sim.add_trace(go.Scatter(
            x=x_halus,
            y=y_halus_saat_ini,
            mode='lines',
            name=label_bar1,
            fill='tozeroy',
            fillcolor='rgba(255, 182, 193, 0.25)',
            line=dict(color='#C71585', width=4),
            hovertemplate="<b>Saat Ini:</b> Rp %{y:,.2f}<extra></extra>"
        ))

        # 3. Titik Spesifik (Marker) pada angka penting: 0%, 30%, 50%, 75%
        fig_sim.add_trace(go.Scatter(
            x=x_asli,
            y=y_saat_ini_asli,
            mode='markers+text',
            text=[f"Rp {val/1e9:.1f}M" for val in y_saat_ini_asli],
            textposition="top center",
            textfont=dict(color='#C71585', size=11, family='Quicksand'),
            marker=dict(size=10, color='#FF69B4', line=dict(color='#C71585', width=2)),
            showlegend=False,
            hovertemplate="Insentif %{x}%: Rp %{y:,.2f}<extra></extra>"
        ))

        fig_sim.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',  
            plot_bgcolor='rgba(255,255,255,0.7)',
            title=dict(text="<b>Simulasi Kurva Parabola Insentif Fiskal</b>", font=dict(size=16, color='#C71585', family="Quicksand")),
            xaxis=dict(
                title='<b>Besaran Insentif Fiskal (%)</b>',
                tickmode='array',
                tickvals=[0, 10, 20, 30, 40, 50, 60, 70, 75],
                ticktext=['0%', '10%', '20%', '30%', '40%', '50%', '60%', '70%', '75%'],
                tickfont=dict(color='#C71585', weight='bold')
            ),
            yaxis=dict(title='<b>Proyeksi Nilai (Rp)</b>', tickfont=dict(color='#C71585')),
            legend=dict(bgcolor='#FFF0F5', bordercolor='#FF1493', borderwidth=1),
            hovermode="x unified"
        )

        st.plotly_chart(fig_sim, use_container_width=True)
    else:
        st.warning("Struktur baris pada Google Sheet simulasi kurang dari 2 baris.")
else:
    st.info("Belum ada data `df_simulasi` yang termuat dari Google Sheet.")
