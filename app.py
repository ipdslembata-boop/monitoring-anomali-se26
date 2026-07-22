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