import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ==========================================
# 1. LOAD DATA DARI URL GOOGLE SHEETS
# ==========================================
url_simulasi = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTs1RqydMwCiImnExjhqC1B_MlnxJaJO5m0UZXOsPPNSyGbphKBK6Wq0bBqpkmmXvkDUMh_LrUcX-Jy/pub?gid=0&single=true&output=csv"

try:
    df_simulasi = pd.read_csv(url_simulasi)
except Exception as e:
    df_simulasi = pd.DataFrame()
    st.error(f"Gagal memuat data dari spreadsheet: {e}")


# ==========================================
# 4. SIMULASI & ANALISIS POTENSI KETETAPAN INSENTIF FISKAL
# ==========================================
st.write("---")
st.subheader("👑 Simulasi Matriks Ketetapan & Potensi Insentif Fiskal (Live dari Spreadsheet)")

if not df_simulasi.empty:
    # Tampilkan Tabel Matriks ala Spreadsheet
    st.markdown("📋 **Tabel Matriks Proyeksi Berdasarkan Insentif Fiskal**")
    
    # Format kolom numerik agar rapi saat ditampilkan
    format_dict = {col: "Rp {:,.2f}" for col in df_simulasi.columns if col not in ['Jumlah Ketetapan', 'KETERANGAN']}
    st.dataframe(df_simulasi.style.format(format_dict, na_rep='-'), use_container_width=True)

    # Visualisasi Grafik dengan Efek Bayangan (Potensi di Belakang)
    st.write("#### 📊 Grafik Perbandingan Ketetapan Saat Ini vs Potensi (Efek Bayangan)")

    kategori_x = ['0%', '30%', '50%', '75%']
    
    # Ambil baris pertama (Ketetapan Saat Ini) dan baris kedua (Potensi Ketetapan) dari spreadsheet
    row_saat_ini = df_simulasi.iloc[0] if len(df_simulasi) > 0 else None
    row_potensi = df_simulasi.iloc[1] if len(df_simulasi) > 1 else None

    if row_saat_ini is not None and row_potensi is not None:
        val_saat_ini = [row_saat_ini.get('0%', 0), row_saat_ini.get('30%', 0), row_saat_ini.get('50%', 0), row_saat_ini.get('75%', 0)]
        val_potensi = [row_potensi.get('0%', 0), row_potensi.get('30%', 0), row_potensi.get('50%', 0), row_potensi.get('75%', 0)]
        
        label_bar1 = str(row_saat_ini.get('Jumlah Ketetapan', 'Ketetapan Saat Ini')) + " (" + str(row_saat_ini.get('KETERANGAN', '')) + ")"
        label_bar2 = str(row_potensi.get('Jumlah Ketetapan', 'Potensi')) + " (" + str(row_potensi.get('KETERANGAN', '')) + ")"

        fig_sim = go.Figure()

        # 1. Grafik Bayangan / Potensi (Di belakang dengan warna transparan & sedikit lebih lebar)
        fig_sim.add_trace(go.Bar(
            x=kategori_x,
            y=val_potensi,
            name=label_bar2,
            marker_color='rgba(255, 105, 180, 0.25)',  # Pink princess transparan
            marker_line_color='#FF1493',               # Pink tua menyala
            marker_line_width=2,
            width=0.6,                                 # Dibuat sedikit lebih lebar agar jadi bayangan latar
            hovertemplate="<b>Potensi:</b> Rp %{y:,.2f}<extra></extra>"
        ))

        # 2. Grafik Utama / Saat Ini (Di depan dengan warna pink princess solid)
        fig_sim.add_trace(go.Bar(
            x=kategori_x,
            y=val_saat_ini,
            name=label_bar1,
            marker_color='#FF69B4',                    # Pink princess solid
            marker_line_color='#C71585',               # Deep pink border
            marker_line_width=1.5,
            width=0.4,                                 # Lebih ramping di bagian depan
            hovertemplate="<b>Saat Ini:</b> Rp %{y:,.2f}<extra></extra>"
        ))

        fig_sim.update_layout(
            barmode='overlay',                         # Tumpang tindih untuk efek bayangan
            paper_bgcolor='rgba(0,0,0,0)',  
            plot_bgcolor='rgba(255,255,255,0.6)',
            title=dict(text="<b>Simulasi Proyeksi Pendapatan Berdasarkan Insentif Fiskal</b>", font=dict(size=16, color='#C71585', family="Quicksand")),
            xaxis=dict(title='<b>Besaran Insentif Fiskal (%)</b>', tickfont=dict(color='#C71585')),
            yaxis=dict(title='<b>Proyeksi Nilai (Rp)</b>', tickfont=dict(color='#C71585')),
            legend=dict(bgcolor='#FFF0F5', bordercolor='#FF1493', borderwidth=1),
            hovermode="x unified"
        )

        st.plotly_chart(fig_sim, use_container_width=True)
    else:
        st.warning("Struktur baris pada Google Sheet simulasi kurang dari 2 baris.")
else:
    st.info("Belum ada data `df_simulasi` yang termuat dari Google Sheet.")
