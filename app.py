<<<<<<< HEAD
import os
import pandas as pd
import streamlit as st

# Konfigurasi Halaman Dashboard (Wajib di baris paling atas)
st.set_page_config(
    page_title="Dashboard Monitoring Anomali Sensus",
    page_icon="📊",
    layout="wide",
)

# Custom Styling CSS Sederhana untuk Tampilan Lebih Bersih
st.markdown("""
    <style>
        .main { background-color: #f8f9fa; }
        .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Dashboard Monitoring Anomali Data Sensus")
st.markdown(
    "Pusat pemantauan anomali data lapangan secara *real-time* berdasarkan level keluarga dan anggota keluarga."
)

# ==========================================
# SIDEBAR: NAVIGASI & FILTER UTAMA
# ==========================================
st.sidebar.header("📁 Navigasi & Filter")

# 1. Pilih Level Anomali (Folder)
level_options = {
    "Anomali Keluarga": "anomalikeluarga",
    "Anomali Anggota Keluarga": "anomalianggotakeluarga",
}
selected_level_label = st.sidebar.selectbox(
    "Pilih Level Analisis", list(level_options.keys())
)
folder_target = level_options[selected_level_label]

# 2. Mendeteksi file CSV/Excel secara otomatis di dalam folder tersebut
if os.path.exists(folder_target):
    files = [
        f
        for f in os.listdir(folder_target)
        if f.endswith(".csv") or f.endswith(".xlsx")
    ]
else:
    files = []

if not files:
    st.warning(
        f"Belum ada file di dalam folder `{folder_target}`. Silakan unggah file"
        " CSV/Excel ke folder tersebut lalu lakukan commit ulang ke GitHub."
    )
else:
    # 3. Pilih Jenis Anomali spesifik berdasarkan nama file
    selected_file = st.sidebar.selectbox(
        "Pilih Jenis Anomali (File)", sorted(files)
    )

    file_path = os.path.join(folder_target, selected_file)


    # Fungsi Membaca File dengan Cache
    @st.cache_data
    def load_data(path):
        if path.endswith(".csv"):
            return pd.read_csv(path)
        else:
            return pd.read_excel(path)


    df = load_data(file_path)

    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Filter Data")

    # Pencarian Mandiri (Search Bar)
    search_query = st.sidebar.text_input(
        "Cari (Nama Petugas / KK / Responden)", ""
    )

    # Deteksi Kolom Petugas secara otomatis
    kolom_petugas = None
    for col in ["NAMAPRINCIPAL", "Nama_Petugas", "Petugas", "nama_petugas"]:
        if col in df.columns:
            kolom_petugas = col
            break

    # Filter Berdasarkan Petugas
    if kolom_petugas:
        list_petugas = ["Semua Petugas"] + list(
            df[kolom_petugas].dropna().unique()
        )
        selected_petugas = st.sidebar.selectbox("Filter Petugas", list_petugas)
        if selected_petugas != "Semua Petugas":
            df = df[df[kolom_petugas] == selected_petugas]

    # Filter Berdasarkan Kecamatan (Jika kolom KEC tersedia)
    if "KEC" in df.columns:
        list_kec = ["Semua Kecamatan"] + list(df["KEC"].dropna().unique())
        selected_kec = st.sidebar.selectbox("Filter Kecamatan", list_kec)
        if selected_kec != "Semua Kecamatan":
            df = df[df["KEC"] == selected_kec]

    # Terapkan Search Query jika diisi
    if search_query:
        # Mencari teks di seluruh kolom string
        mask = df.astype(str).apply(
            lambda x: x.str.contains(search_query, case=False, na=False)
        ).any(axis=1)
        df = df[mask]

    # ==========================================
    # MAIN CONTENT: KARTU METRIK & VISUALISASI
    # ==========================================

    # Metrik Ringkasan (KPI Cards)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="Total Temuan Anomali",
            value=len(df),
            delta="Perhatian Khusus",
        )
    with col2:
        if kolom_petugas:
            st.metric(
                label="Petugas Terlibat", value=df[kolom_petugas].nunique()
            )
        else:
            st.metric(label="Status Saringan", value="Aktif")
    with col3:
        if "KEC" in df.columns:
            st.metric(
                label="Cakupan Kecamatan", value=df["KEC"].nunique()
            )
        else:
            st.metric(label="Tipe Data", value="Tabel Master")

    st.markdown("---")

    # Grafik Ringkasan Sederhana (Jika kolom petugas ada)
    if kolom_petugas and not df.empty:
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.subheader("📈 Top 5 Petugas dengan Anomali Terbanyak")
            top_petugas = df[kolom_petugas].value_counts().head(5)
            st.bar_chart(top_petugas)

        with col_chart2:
            if "KEC" in df.columns:
                st.subheader("📍 Anomali Berdasarkan Kecamatan")
                top_kec = df["KEC"].value_counts().head(5)
                st.bar_chart(top_kec, color="#ff4b4b")
            else:
                st.info(
                    "Tip: Tambahkan kolom 'KEC' pada hasil SQL Anda untuk"
                    " melihat grafik sebaran wilayah."
                )

    st.markdown("---")

    # ==========================================
    # TABEL RINCIAN INTERAKTIF
    # ==========================================
    file_title = (
        selected_file.replace(".csv", "").replace(".xlsx", "").replace("_", " ")
    )
    st.subheader(f"📋 Tabel Rincian: {file_title.title()}")
    st.caption(
        "Anda dapat melakukan sorting (mengurutkan) dengan mengklik header"
        " kolom pada tabel di bawah."
    )

    # Konfigurasi agar kolom link otomatis aktif bisa diklik
    column_configs = {}
    for col in df.columns:
        if "link" in col.lower() or "url" in col.lower():
            column_configs[col] = st.column_config.LinkColumn(
                col, display_text="Buka Assignment 🔗"
            )

    st.dataframe(
        df,
        column_config=column_configs,
        use_container_width=True,
        hide_index=True,
    )

    # Tombol Download Data Filtered ke CSV
    st.markdown("### 📥 Unduh Laporan")
    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Data Terfiltrasi (CSV)",
        data=csv_data,
        file_name=f"laporan_{selected_file}",
        mime="text/csv",
    )
=======
import os
import pandas as pd
import streamlit as st

# Konfigurasi Halaman Dashboard
st.set_page_config(
    page_title="Dashboard Anomali Sensus", page_icon="📊", layout="wide"
)

st.title("📊 Dashboard Monitoring Anomali Data Sensus")
st.markdown(
    "Aplikasi pemantauan anomali data lapangan berdasarkan level keluarga dan"
    " anggota keluarga."
)

# Sidebar Navigasi & Filter
st.sidebar.header("📁 Pengaturan Data")

# 1. Pilih Level Anomali (Folder)
level_options = {
    "Anomali Keluarga": "anomalikeluarga",
    "Anomali Anggota Keluarga": "anomalianggotakeluarga",
}
selected_level_label = st.sidebar.selectbox(
    "Pilih Level Analisis", list(level_options.keys())
)
folder_target = level_options[selected_level_label]

# 2. Mendeteksi file CSV/Excel secara otomatis di dalam folder tersebut
if os.path.exists(folder_target):
  files = [
      f
      for f in os.listdir(folder_target)
      if f.endswith(".csv") or f.endswith(".xlsx")
  ]
else:
  files = []

if not files:
  st.warning(
      f"Belum ada file di dalam folder `{folder_target}`. Silakan unggah file"
      " CSV/Excel ke folder tersebut."
  )
else:
  # 3. Pilih Jenis Anomali spesifik berdasarkan nama file
  selected_file = st.sidebar.selectbox(
      "Pilih Jenis Anomali (File)", sorted(files)
  )

  file_path = os.path.join(folder_target, selected_file)


  # Membaca file (mendukung CSV dan Excel)
  @st.cache_data
  def load_data(path):
    if path.endswith(".csv"):
      return pd.read_csv(path)
    else:
      return pd.read_excel(path)


  df = load_data(file_path)

  # Filter Berdasarkan Petugas (Jika kolom NAMAPRINCIPAL atau Nama_Petugas tersedia)
  kolom_petugas = None
  for col in ["NAMAPRINCIPAL", "Nama_Petugas", "Petugas", "nama_petugas"]:
    if col in df.columns:
      kolom_petugas = col
      break

  if kolom_petugas:
    list_petugas = ["Semua Petugas"] + list(df[kolom_petugas].dropna().unique())
    selected_petugas = st.sidebar.selectbox("Filter Petugas", list_petugas)
    if selected_petugas != "Semua Petugas":
      df = df[df[kolom_petugas] == selected_petugas]

  # Metrik Ringkasan (KPI Cards)
  col1, col2 = st.columns(2)
  with col1:
    st.metric("Total Temuan Anomali", len(df))
  with col2:
    if kolom_petugas:
      st.metric("Jumlah Petugas Terlibat", df[kolom_petugas].nunique())
    else:
      st.metric("Status Data", "Aktif")

  st.markdown("---")

  # Tampilkan Tabel Rincian Data
  st.subheader(
      f"📋 Rincian Data:"
      f" {selected_file.replace('.csv', '').replace('.xlsx', '')}"
  )

  # Konfigurasi agar kolom 'Link' atau yang berbau URL bisa diklik otomatis (jika ada)
  column_configs = {}
  for col in df.columns:
    if "link" in col.lower() or "url" in col.lower():
      column_configs[col] = st.column_config.LinkColumn(
          col, display_text="Buka Link 🔗"
      )

  st.dataframe(df, column_config=column_configs, use_container_width=True)
>>>>>>> 86f3811a527560900f2cab5ef03630103bb98a8e
