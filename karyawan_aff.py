import pandas as pd
import networkx as nx
from pyvis.network import Network
from Levenshtein import ratio
import re

# === 1. BACA DATA EXCEL ===
file_path = "data_karyawan.xlsx"  # Ganti dengan nama file kamu
df = pd.read_excel(file_path)

# === 2. NORMALISASI DATA NAMA ===
def extract_marga(nama):
    """Ambil kata terakhir dari nama (biasanya marga atau nama keluarga)."""
    if not isinstance(nama, str):
        return ""
    nama = nama.strip()
    parts = nama.split()
    return parts[-1].lower() if parts else ""

df["Marga"] = df["Nama"].apply(extract_marga)

# === 3. SIAPKAN DATA UNTUK PEMBANDING ===
pairs = []
n = len(df)

def get_usia(tanggal_lahir):
    try:
        return pd.Timestamp.now().year - pd.to_datetime(tanggal_lahir).year
    except:
        return None

df["Usia"] = df["Tanggal Lahir"].apply(get_usia)

# === 4. BANDINGKAN SETIAP PASANG KARYAWAN ===
for i in range(n):
    for j in range(i + 1, n):
        nama1, nama2 = df.loc[i, "Nama"], df.loc[j, "Nama"]
        dom1, dom2 = str(df.loc[i, "Domisili"]).lower(), str(df.loc[j, "Domisili"]).lower()
        marga1, marga2 = df.loc[i, "Marga"], df.loc[j, "Marga"]
        usia1, usia2 = df.loc[i, "Usia"], df.loc[j, "Usia"]

        # Similarity nama (pakai Levenshtein)
        nama_sim = ratio(nama1.lower(), nama2.lower())

        # Kondisi potensi hubungan keluarga
        same_marga = marga1 == marga2 and marga1 != ""
        same_domisili = dom1 and dom1 == dom2
        usia_diff = abs(usia1 - usia2) if usia1 and usia2 else None

        relation = None

        if same_domisili and usia_diff is not None:
            if usia_diff <= 5 and same_marga:
                relation = "Saudara Kandung"
            elif 18 <= usia_diff <= 35 and same_marga:
                relation = "Orang Tua/Anak"
            elif usia_diff < 10 and not same_marga:
                relation = "Suami/Istri"
            elif same_domisili:
                relation = "Satu Rumah"

        elif same_marga and nama_sim > 0.6:
            relation = "Kemungkinan Keluarga"

        if relation:
            pairs.append({
                "Nama 1": nama1,
                "Nama 2": nama2,
                "Marga Sama": same_marga,
                "Domisili Sama": same_domisili,
                "Selisih Usia": usia_diff,
                "Hubungan": relation
            })

# === 5. BUAT GRAF JARINGAN ===
G = nx.Graph()

# Tambahkan node untuk setiap karyawan
for idx, row in df.iterrows():
    G.add_node(row["Nama"], title=f"Domisili: {row['Domisili']}<br>Usia: {row['Usia']}")

# Tambahkan edge untuk setiap hubungan yang terdeteksi
for p in pairs:
    G.add_edge(p["Nama 1"], p["Nama 2"], title=p["Hubungan"], label=p["Hubungan"])

# === 6. VISUALISASI DENGAN PYVIS ===
net = Network(height="800px", width="100%", bgcolor="#ffffff", font_color="black")
net.from_nx(G)

# Warna berdasarkan jenis hubungan
for edge in net.edges:
    if "Suami/Istri" in edge["title"]:
        edge["color"] = "red"
    elif "Saudara" in edge["title"]:
        edge["color"] = "blue"
    elif "Anak" in edge["title"]:
        edge["color"] = "green"
    elif "Satu Rumah" in edge["title"]:
        edge["color"] = "orange"
    else:
        edge["color"] = "gray"

# Simpan grafik ke file HTML
net.save_graph("grafik_afiliasi_karyawan.html")
print("✅ Grafik afiliasi karyawan telah dibuat: grafik_afiliasi_karyawan.html")

# === 7. (OPSIONAL) SIMPAN HASIL KE EXCEL ===
pd.DataFrame(pairs).to_excel("hasil_deteksi_keluarga.xlsx", index=False)
print("✅ Hasil deteksi disimpan ke hasil_deteksi_keluarga.xlsx")
