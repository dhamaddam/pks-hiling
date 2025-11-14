import pandas as pd
import plotly.express as px
from itertools import product

# === 1. BACA FILE EXCEL ===
file_path = "data_spl.xlsx"  # ubah ke nama file kamu
df = pd.read_excel(file_path)

# === 2. FORMAT DAN BERSIHKAN DATA ===
# Pastikan kolom yang digunakan ada
required_cols = [
    'Nomor SPL', 'Nama Bagian', 'Tanggal SPL',
    'Total Jam Permohonan', 'Total Tarif Permohonan'
]
for col in required_cols:
    if col not in df.columns:
        raise KeyError(f"Kolom '{col}' tidak ditemukan di file Excel.")

# Format tanggal
df['Tanggal SPL'] = pd.to_datetime(df['Tanggal SPL'], errors='coerce')

# Bersihkan teks pada kolom "Nama Bagian"
df['Nama Bagian'] = (
    df['Nama Bagian']
    .astype(str)
    .str.strip()
    .str.title()
    .replace(['Nan', 'None', ''], 'Tidak Diketahui')
)

# Ubah format jam dari "15:36" jadi float jam
def parse_jam(value):
    if isinstance(value, str) and ':' in value:
        jam, menit = value.split(':')
        return int(jam) + int(menit) / 60
    try:
        return float(value)
    except:
        return 0

df['Total Jam Permohonan'] = df['Total Jam Permohonan'].apply(parse_jam)

# Ubah format tarif jadi float
df['Total Tarif Permohonan'] = (
    df['Total Tarif Permohonan']
    .astype(str)
    .str.replace('.', '', regex=False)
    .astype(float)
)

# === 3. TAMBAH KOLOM BULAN ===
df['Bulan'] = df['Tanggal SPL'].dt.strftime('%B %Y')

# === 4. AGREGASI DATA ===
agg = df.groupby(['Bulan', 'Nama Bagian']).agg(
    Frekuensi_Lembur=('Nomor SPL', 'count'),
    Total_Jam=('Total Jam Permohonan', 'sum'),
    Total_Tarif=('Total Tarif Permohonan', 'sum')
).reset_index()

# === 5. TAMPILKAN SEMUA SUB BAGIAN MESKIPUN 0 ===
all_bagian = sorted(df['Nama Bagian'].unique())
all_bulan = sorted(df['Bulan'].dropna().unique(), key=lambda x: pd.to_datetime(x, format='%B %Y'))

full_index = pd.DataFrame(product(all_bulan, all_bagian), columns=['Bulan', 'Nama Bagian'])
agg = full_index.merge(agg, on=['Bulan', 'Nama Bagian'], how='left').fillna(0)

# === 6. BUAT HTML INTERAKTIF ===
html_template = """
<html>
<head>
    <title>Analisis Lembur per Bagian</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
        }}
        select {{
            padding: 8px;
            font-size: 14px;
            margin-bottom: 20px;
        }}
        h2 {{
            color: #2c3e50;
        }}
    </style>
</head>
<body>

<h2>📊 Analisis Lembur per Bagian</h2>
<label>Pilih Bulan: </label>
<select id="bulan" onchange="updateGraph()">
    {options}
</select>

<div id="grafik_frekuensi"></div>
<div id="grafik_jam"></div>
<div id="grafik_tarif"></div>

<script>
var data = {agg_json};

function updateGraph() {{
    var bulanDipilih = document.getElementById('bulan').value;
    var filtered = data.filter(d => d.Bulan === bulanDipilih);

    var bagian = filtered.map(d => d['Nama Bagian']);
    var frek = filtered.map(d => d['Frekuensi_Lembur']);
    var jam = filtered.map(d => d['Total_Jam']);
    var tarif = filtered.map(d => d['Total_Tarif']);

    var trace1 = {{
        x: bagian,
        y: frek,
        type: 'bar',
        marker: {{color: '#3498db'}}
    }};

    var trace2 = {{
        x: bagian,
        y: jam,
        type: 'bar',
        marker: {{color: '#27ae60'}}
    }};

    var trace3 = {{
        x: bagian,
        y: tarif,
        type: 'bar',
        marker: {{color: '#e67e22'}}
    }};

    var layout1 = {{ title: 'Frekuensi Lembur per Bagian (' + bulanDipilih + ')', xaxis: {{title: 'Bagian'}}, yaxis: {{title: 'Frekuensi'}} }};
    var layout2 = {{ title: 'Total Jam Lembur per Bagian (' + bulanDipilih + ')', xaxis: {{title: 'Bagian'}}, yaxis: {{title: 'Jam'}} }};
    var layout3 = {{ title: 'Total Tarif Lembur per Bagian (' + bulanDipilih + ')', xaxis: {{title: 'Bagian'}}, yaxis: {{title: 'Tarif (Rp)'}} }};

    Plotly.newPlot('grafik_frekuensi', [trace1], layout1);
    Plotly.newPlot('grafik_jam', [trace2], layout2);
    Plotly.newPlot('grafik_tarif', [trace3], layout3);
}}

updateGraph(); // tampilkan awal
</script>

</body>
</html>
"""

# === 7. EXPORT KE HTML ===
options_html = "\n".join([f'<option value="{bulan}">{bulan}</option>' for bulan in all_bulan])
agg_json = agg.to_dict(orient='records')

with open("hasil_analisis_lembur.html", "w", encoding="utf-8") as f:
    f.write(html_template.format(options=options_html, agg_json=agg_json))

print("✅ File 'hasil_analisis_lembur.html' berhasil dibuat! Buka di browser untuk melihat hasilnya.")
