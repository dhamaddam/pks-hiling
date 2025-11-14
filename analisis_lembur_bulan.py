import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json

# === 1. BACA FILE EXCEL ===
file_path = 'data_spl.xlsx'  # ubah sesuai nama file kamu
df = pd.read_excel(file_path)

# === 2. PILIH KOLOM YANG DIPERLUKAN ===
df = df[['Nomor SPL', 'Nama Bagian', 'Total Jam Permohonan', 'Total Tarif Permohonan', 'Tanggal SPL']]

# === 3. KONVERSI FORMAT DATA ===
def parse_jam(value):
    """Ubah format '15:36' jadi 15.6 jam"""
    if isinstance(value, str) and ':' in value:
        jam, menit = value.split(':')
        return int(jam) + int(menit) / 60
    try:
        return float(value)
    except:
        return 0

# Bersihkan data
df['Total Jam Permohonan'] = df['Total Jam Permohonan'].apply(parse_jam)
df['Total Tarif Permohonan'] = (
    df['Total Tarif Permohonan']
    .astype(str)
    .str.replace('.', '', regex=False)
    .astype(float)
)
df['Tanggal SPL'] = pd.to_datetime(df['Tanggal SPL'], errors='coerce')

# === 4. TAMBAH KOLOM BULAN ===
df['Bulan'] = df['Tanggal SPL'].dt.strftime('%B %Y')

# === 5. AGREGASI DATA PER BAGIAN DAN BULAN ===
agg = df.groupby(['Bulan', 'Nama Bagian']).agg(
    Frekuensi_Lembur=('Nomor SPL', 'count'),
    Total_Jam=('Total Jam Permohonan', 'sum'),
    Total_Tarif=('Total Tarif Permohonan', 'sum')
).reset_index()

# === 6. URUTKAN BERDASARKAN TOTAL TARIF (DALAM SETIAP BULAN) ===
agg = agg.sort_values(['Bulan', 'Total_Tarif'], ascending=[True, False])

# === 7. SIAPKAN DATA UNTUK HTML ===
bulan_list = sorted(agg['Bulan'].unique(), key=lambda x: pd.to_datetime(x, format='%B %Y'))
agg_json = agg.to_dict(orient='records')

# === 8. TEMPLATE HTML INTERAKTIF ===
html_template = """
<html>
<head>
    <title>Analisis Lembur Per Bagian - Filter Bulanan</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 30px;
        }}
        select {{
            padding: 8px;
            font-size: 15px;
            margin-bottom: 20px;
        }}
        h2 {{
            color: #2c3e50;
        }}
        table {{
            border-collapse: collapse;
            width: 80%;
            margin-bottom: 30px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
        }}
        th {{
            background-color: #f4f4f4;
        }}
    </style>
</head>
<body>

<h2>📊 Analisis Lembur Per Bagian</h2>
<label><b>Pilih Bulan:</b></label>
<select id="bulanSelect" onchange="updateDashboard()">
    {bulan_options}
</select>

<div id="tabel_rekap"></div>
<div id="grafik1"></div>
<div id="grafik2"></div>
<div id="grafik3"></div>

<script>
var data = {agg_json};

function updateDashboard() {{
    var bulan = document.getElementById('bulanSelect').value;
    var filtered = data.filter(d => d.Bulan === bulan);

    // === Buat Tabel ===
    var tableHTML = "<table><tr><th>Nama Bagian</th><th>Frekuensi</th><th>Total Jam</th><th>Total Tarif</th></tr>";
    filtered.forEach(d => {{
        tableHTML += `<tr>
            <td>${{d['Nama Bagian']}}</td>
            <td>${{d['Frekuensi_Lembur']}}</td>
            <td>${{d['Total_Jam'].toFixed(2)}}</td>
            <td>${{d['Total_Tarif'].toLocaleString('id-ID')}}</td>
        </tr>`;
    }});
    tableHTML += "</table>";
    document.getElementById('tabel_rekap').innerHTML = "<h3>Rekapitulasi Lembur Bulan " + bulan + "</h3>" + tableHTML;

    // === Siapkan Data Grafik ===
    var bagian = filtered.map(d => d['Nama Bagian']);
    var frek = filtered.map(d => d['Frekuensi_Lembur']);
    var jam = filtered.map(d => d['Total_Jam']);
    var tarif = filtered.map(d => d['Total_Tarif']);

    // Grafik 1: Frekuensi & Jam
    var trace1 = {{
        x: bagian,
        y: frek,
        type: 'bar',
        name: 'Frekuensi Lembur',
        marker: {{color: '#3498db'}}
    }};
    var trace2 = {{
        x: bagian,
        y: jam,
        type: 'line',
        name: 'Total Jam',
        marker: {{color: '#e67e22'}}
    }};
    Plotly.newPlot('grafik1', [trace1, trace2], {{
        title: 'Frekuensi & Total Jam per Bagian (' + bulan + ')',
        barmode: 'group',
        xaxis: {{title: 'Nama Bagian'}},
        yaxis: {{title: 'Nilai'}},
        template: 'plotly_white'
    }});

    // Grafik 2: Total Tarif
    var trace3 = {{
        x: bagian,
        y: tarif,
        type: 'bar',
        name: 'Total Tarif',
        marker: {{color: '#2ecc71'}}
    }};
    Plotly.newPlot('grafik2', [trace3], {{
        title: 'Total Tarif Permohonan per Bagian (' + bulan + ')',
        xaxis: {{title: 'Nama Bagian'}},
        yaxis: {{title: 'Total Tarif (Rp)'}},
        template: 'plotly_white'
    }});

    // Grafik 3: Pie Chart
    var trace4 = {{
        labels: bagian,
        values: tarif,
        type: 'pie',
        hole: 0.4
    }};
    Plotly.newPlot('grafik3', [trace4], {{
        title: 'Persentase Total Tarif per Bagian (' + bulan + ')',
        template: 'plotly_white'
    }});
}}

updateDashboard(); // jalankan pertama kali
</script>
</body>
</html>
"""

# === 9. SIMPAN FILE HTML ===
os.makedirs("output", exist_ok=True)
output_html = "output/analisis_lembur_bulanan.html"

bulan_options = "\n".join([f'<option value="{b}">{b}</option>' for b in bulan_list])

with open(output_html, "w", encoding="utf-8") as f:
    f.write(html_template.format(bulan_options=bulan_options, agg_json=json.dumps(agg_json)))

print(f"\n✅ File berhasil dibuat: {output_html}")
print("💡 Buka di browser untuk melihat dashboard interaktif.")
