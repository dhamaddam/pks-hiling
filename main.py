from src.helper.Logfile import LogFile
from flask_cors import CORS
from flask_restful import Resource, Api
from flask_sslify import SSLify
from flask import Flask,jsonify,session, request, redirect, url_for, render_template, flash
import csv
import os
import pandas as pd
from flask import send_file
import os

app = Flask(__name__)
app.secret_key = 'nakamichi!@#' 
CORS(app)

def hello():
      return render_template('homepage.html')

def login():
    return render_template('login.html') 

def dashboard():
    return render_template('dashboard.html', username="Admin")

@app.route('/download-excel')
def download_excel():
    csv_file = 'hasil_nsp.csv'
    excel_file = 'hasil_nsp.xlsx'

    # Pastikan file CSV ada
    if not os.path.exists(csv_file):
        return "File tidak ditemukan", 404

    # Konversi CSV ke Excel
    df = pd.read_csv(csv_file)
    df.to_excel(excel_file, index=False)

    # Kirim file ke client
    return send_file(excel_file, as_attachment=True)

@app.route('/logout')
def logout():
    session.clear()  # atau session.pop('user', None)
    return redirect(url_for('login'))

def lihat_hasil_sortasi():
    data = []
    csv_file = 'hasil_nsp.csv'
    try:
        with open(csv_file, mode='r') as f:
            reader = csv.reader(f)
            headers = next(reader)  # Baris pertama sebagai header
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        headers = []
        data = []

    return render_template('lihat_hasil_sortasi.html', username="Admin", headers=headers, data=data)

def sortasi_panen():
    if request.method == 'POST':
        form = request.form

        # Ambil nilai dari form
        try:
            fpmt = float(form['fpmt'])
            bmt = float(form['bmt'])
            fpkm = float(form['fpkm'])
            bkm = float(form['bkm'])
            fpm = float(form['fpm'])
            bm = float(form['bm'])
            fplm = float(form['fplm'])
            blm = float(form['blm'])
            bn = float(form['bn'])
        except ValueError:
            return render_template('sortasi_panen.html', error="Masukkan angka yang valid")

        # Hitung NSP dan NSP’
        nsp = fpmt * bmt + fpkm * bkm + fpm * bm + fplm * blm
        nsp_prime = nsp * bn

        if form['action'] == 'simpan':
            # Simpan ke CSV
            data = [
                form['perusahaan'],
                form['kebun'],
                form['afdelling'],
                fpmt, bmt, fpkm, bkm, fpm, bm, fplm, blm, bn,
                nsp, nsp_prime
            ]
            csv_file = 'hasil_nsp.csv'
            file_exists = os.path.isfile(csv_file)

            with open(csv_file, mode='a', newline='') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow([
                        "Perusahaan", "Kebun", "Afdelling", "FPmt", "BMt", "FPKM", "BKM", "FPM", "BM", "FPLM", "BLM", "BN", "NSP", "NSP'"
                    ])
                writer.writerow(data)

        return render_template('sortasi_panen.html', nsp=round(nsp, 2), nsp_prime=round(nsp_prime, 2))

    return render_template('sortasi_panen.html', username="Admin")


def login_match():
    logging = LogFile("daemon")
    logging.write("info","try to login")
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username == 'admin_ppks' and password == 'ppks123':
        session['user'] = 'admin'
        return redirect(url_for('dashboard'))
        # return "Login berhasil!"
    else:
        flash("Username atau password salah!")
        return redirect(url_for('index'))
    
app.add_url_rule('/', view_func=hello,methods=['GET','POST'])
app.add_url_rule('/login', view_func=login,methods=['GET','POST'])
app.add_url_rule('/login_match', view_func=login_match,methods=['GET','POST'])
app.add_url_rule('/dashboard', view_func=dashboard,methods=['GET','POST'])
app.add_url_rule('/sortasi_panen',view_func=sortasi_panen,methods=['GET','POST'])
app.add_url_rule('/lihat_hasil_sortasi',view_func=lihat_hasil_sortasi, methods=['GET','POST'])

if __name__ == '__main__':
    logging = LogFile("daemon")
    # app.run(port=5001) 
    # app.run(debug=True, port=5001)
    app.run(host='0.0.0.0')