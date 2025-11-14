import tkinter as tk

def tombol_ditekan():
    label_hasil.config(text="Halo, Sawit Digital!")

# Jendela utama
root = tk.Tk()
root.title("Contoh Tkinter")

# Komponen
label_hasil = tk.Label(root, text="Selamat datang!")
label_hasil.pack(pady=10)

tombol = tk.Button(root, text="Tekan Saya", command=tombol_ditekan)
tombol.pack(pady=5)

# Jalankan aplikasi
root.mainloop()

