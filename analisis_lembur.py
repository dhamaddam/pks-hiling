import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# === 1. BACA FILE EXCEL ===
file_path = 'data_spl.xlsx'  # ubah nama file sesuai data kamu
df = pd.read_excel(file_path)

# === 2. PILIH KOLOM YANG DIPERLUKAN ===
df = df[['Nomor SPL', 'Nama Bagian', 'Total Jam Permohonan', 'Total Tarif Permohonan','Tanggal SPL']]

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

df['Total Jam Permohonan'] = df['Total Jam Permohonan'].apply(parse_jam)
df['Total Tarif Permohonan'] = (
    df['Total Tarif Permohonan']
    .astype(str)
    .str.replace('.', '', regex=False)
    .astype(float)
)

# === 4. HITUNG AGREGASI ===
agg = df.groupby('Nama Bagian').agg(
    Frekuensi_Lembur=('Nomor SPL', 'count'),
    Total_Jam=('Total Jam Permohonan', 'sum'),
    Total_Tarif=('Total Tarif Permohonan', 'sum')
).reset_index()

agg = agg.sort_values(by='Total_Tarif', ascending=False)
# === 5. BUAT VISUALISASI INTERAKTIF ===
# Grafik 1: Frekuensi & Total Jam Lembur
fig1 = go.Figure()
fig1.add_bar(x=agg['Nama Bagian'], y=agg['Frekuensi_Lembur'], name='Frekuensi Lembur')
fig1.add_trace(go.Scatter(
    x=agg['Nama Bagian'], y=agg['Total_Jam'],
    mode='lines+markers', name='Total Jam Lembur', line=dict(color='orange', width=3)
))
fig1.update_layout(
    title='Perbandingan Frekuensi & Total Jam Lembur per Bagian',
    xaxis_title='Nama Bagian',
    yaxis_title='Nilai',
    template='plotly_white'
)

# Grafik 2: Total Tarif per Bagian
fig2 = px.bar(
    agg,
    x='Nama Bagian', y='Total_Tarif',
    title='Total Tarif Permohonan per Bagian',
    labels={'Total_Tarif': 'Total Tarif (Rp)'},
    color='Nama Bagian'
)

# Grafik 3: Pie Chart perbandingan tarif
fig3 = px.pie(
    agg,
    names='Nama Bagian', values='Total_Tarif',
    title='Persentase Total Tarif Lembur per Bagian',
    hole=0.4
)

# === 6. SIMPAN KE FILE HTML ===
os.makedirs("output", exist_ok=True)
output_html = "output/analisis_lembur.html"

with open(output_html, "w") as f:
    f.write("<h1 style='font-family:sans-serif;'>📊 Analisis Lembur Per Bagian</h1>")
    f.write("<h3>Data Rekapitulasi</h3>")
    f.write(agg.to_html(index=False, justify='center', border=0))
    f.write("<hr><h3>Grafik Perbandingan Frekuensi & Total Jam</h3>")
    f.write(fig1.to_html(full_html=False, include_plotlyjs='cdn'))
    f.write("<hr><h3>Grafik Total Tarif per Bagian</h3>")
    f.write(fig2.to_html(full_html=False, include_plotlyjs=False))
    f.write("<hr><h3>Persentase Tarif (Pie Chart)</h3>")
    f.write(fig3.to_html(full_html=False, include_plotlyjs=False))

print(f"\n✅ File berhasil dibuat: {output_html}")
print("💡 Buka file ini di browser untuk melihat hasil interaktif.")
