# ==========================================
# 4. SIMULASI & ANALISIS POTENSI KETETAPAN INSENTIF FISKAL (DARI GOOGLE SHEET)
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

        # 1. Grafik Bayangan (Potensi Ketetapan - di belakang dengan warna transparan)
        fig_sim.add_trace(go.Bar(
            x=kategori_x,
            y=val_potensi,
            name=label_bar2,
            marker_color='rgba(216, 191, 216, 0.4)',  # Ungu lavender transparan
            marker_line_color='#9370DB',
            marker_line_width=1.5,
            hovertemplate="<b>Potensi:</b> Rp %{y:,.2f}<extra></extra>"
        ))

        # 2. Grafik Utama (Ketetapan Saat Ini - di depan dengan warna solid)
        fig_sim.add_trace(go.Bar(
            x=kategori_x,
            y=val_saat_ini,
            name=label_bar1,
            marker_color='#FF69B4',  # Pink princess solid
            marker_line_color='#C71585',
            marker_line_width=1.5,
            hovertemplate="<b>Saat Ini:</b> Rp %{y:,.2f}<extra></extra>"
        ))

        fig_sim.update_layout(
            barmode='overlay',  # Membuat grafik saling tumpang tindih (efek bayangan latar)
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(255,255,255,0.5)',
            title=dict(text="Simulasi Proyeksi Pendapatan Berdasarkan Besaran Insentif Fiskal", font=dict(size=16, color='#C71585')),
            xaxis=dict(title='Besaran Insentif Fiskal (%)', tickfont=dict(color='#C71585')),
            yaxis=dict(title='Proyeksi Nilai (Rp)', tickfont=dict(color='#C71585')),
            legend=dict(bgcolor='#FFF0F5', bordercolor='#FF1493', borderwidth=1),
            hovermode="x unified"
        )

        st.plotly_chart(fig_sim, use_container_width=True)
    else:
        st.warning("Struktur baris pada Google Sheet simulasi kurang dari 2 baris.")
else:
    st.info("Belum ada data simulasi yang termuat dari Google Sheet. Pastikan URL `url_simulasi` sudah diisi dengan benar.")
