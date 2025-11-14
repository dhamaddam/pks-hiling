import matplotlib.pyplot as plt

# Data
providers = ['Starlink', 'FiberStar', 'Nusanet','Hypernet', 'ICON+']
biaya_tahunan = [22840000, 44888400, 34636000,58500000, 60000000]

# Grafik horizontal
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(providers, biaya_tahunan, color='mediumseagreen')

# Tampilkan label nilai
for bar in bars:
    width = bar.get_width()
    ax.text(width + 1_000_000, bar.get_y() + bar.get_height()/2,
            f"{width:,.0f}", va='center')

ax.set_title("Simulasi Total Biaya Internet Selama 1 Tahun", fontsize=14)
ax.set_xlabel("Total Biaya untuk 1 Tahun (IDR)")
ax.invert_yaxis()
plt.tight_layout()
plt.show()
