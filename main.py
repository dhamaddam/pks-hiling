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
import requests
from src.helper.Config import Config

from src.dashboard.dashboard import Dashboard,dashboard_module
from src.mobile.serve_produksi import serveProduksi,produksi_module
from src.mobile.serve_vegetatif import serveVegetatif,vegetatif_module
from src.mobile.serve_segregasi import serveSegregasi,segregasi_module
from src.mobile.serve_sexratio import serveSexRatio,sexratio_module
from src.mobile.serve_sensus_tanaman import serveSensusTanaman,sensus_tanaman_module
from src.mobile.serve_master_data import serveMasterData,master_data_module
from src.mobile.serve_antan import serveAnalisaTandan,analisa_tandan_module


main = Dashboard()
apiProduksi = serveProduksi()
apiVegetatif = serveVegetatif()
apiSegregasi = serveSegregasi()
apiSexratio = serveSexRatio()
apiSensusTanaman = serveSensusTanaman()
apiMasterData = serveMasterData()
apiAnalisaTandan = serveAnalisaTandan()


app = Flask(__name__)



app.secret_key = 'nakamichi!@#' 
CORS(app)

app.register_blueprint(dashboard_module, url_prefix='/dashboard')
app.register_blueprint(produksi_module, url_prefix='/produksi')
app.register_blueprint(vegetatif_module, url_prefix='/vegetatif')
app.register_blueprint(segregasi_module, url_prefix='/segregasi')
app.register_blueprint(sexratio_module, url_prefix='/sexratio')
app.register_blueprint(sensus_tanaman_module, url_prefix='/sensus_tanaman')
app.register_blueprint(master_data_module, url_prefix='/master_data')
app.register_blueprint(analisa_tandan_module, url_prefix='/analisa_tandan')

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


from flask import render_template, request
import math

def lihat_data_pegawai():
    db = Config()
    df = db.query("SELECT nik, nama, tgl_kerja, ket_posisi, alamat, foto FROM pegawai")

    if df is None or df.empty:
        headers = []
        data = []
        page = 1
        total_pages = 1
    else:
        # Ambil parameter pencarian dan pagination dari query string
        search = request.args.get('search', '').lower()
        page = int(request.args.get('page', 1))
        per_page = 10
        
        if search:
            df = df[df['nama'].str.lower().str.contains(search)]
        
        base_url = "https://e-sip.iopri.co.id/assets/Absen/"
        
       
        # Ganti fotoAbsen dengan URL jika ada, else None
        df['foto'] = df['foto'].apply(check_image_exist)
        headers = df.columns.tolist()
        all_data = df.values.tolist()

        # Pagination
        page = int(request.args.get('page', 1))  # default page = 1
        per_page = 10
        total_data = len(all_data)
        total_pages = math.ceil(total_data / per_page)

        # Slicing data per halaman
        start = (page - 1) * per_page
        end = start + per_page
        data = all_data[start:end]
        

    return render_template(
        'lihat_data_pegawai.html',
        username="Admin",
        headers=headers,
        data=data,
        page=page,
        total_pages=total_pages
    )
def check_image_exist(filename):
    # base_url = "https://e-sip.iopri.co.id/assets/Absen/"
    base_url = "https://sip.rpn.co.id/file/foto/"
    if not filename or pd.isna(filename):
        return False
    url = base_url + filename
    try:
        response = requests.head(url, timeout=3)
        if response.status_code == 200:
            return url
        else:
            return False
    except requests.RequestException:
        return False
        
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
        return redirect(url_for('login'))

app.add_url_rule('/', view_func=hello,methods=['GET','POST'])
app.add_url_rule('/login', view_func=login,methods=['GET','POST'])
app.add_url_rule('/login_match', view_func=login_match,methods=['GET','POST'])
app.add_url_rule('/dashboard', view_func=dashboard,methods=['GET','POST'])
app.add_url_rule('/sortasi_panen',view_func=main.sortasi_panen,methods=['GET','POST'])
app.add_url_rule('/lihat_hasil_sortasi',view_func=main.lihat_hasil_sortasi, methods=['GET','POST'])
app.add_url_rule('/lihat_data_pegawai',view_func=lihat_data_pegawai, methods=['GET','POST'])

app.add_url_rule('/master_data', view_func=main.master_data, methods=['GET','POST'])
app.add_url_rule('/analisa_tandan', view_func=main.analisa_tandan, methods=['GET','POST'])
app.add_url_rule('/produksi', view_func=main.produksi, methods=['GET','POST'])
app.add_url_rule('/vegetatif_tanaman', view_func=main.vegetatif_tanaman, methods=['GET','POST'])
app.add_url_rule('/sensus_tanaman', view_func=main.sensus_tanaman, methods=['GET','POST'])
app.add_url_rule('/sex_ratio', view_func=main.sex_ratio, methods=['GET','POST'])
app.add_url_rule('/segregasi', view_func=main.segregasi, methods=['GET','POST'])
app.add_url_rule('/export_master_data_xls', view_func=main.export_master_data_xls)
app.add_url_rule('/export_analisa_tandan_xls', view_func=main.export_analisa_tandan_xls)
app.add_url_rule('/export_produksi_xls', view_func=main.export_produksi_xls)

if __name__ == '__main__':
    logging = LogFile("daemon")
    # app.run(port=5001) 
    # app.run(debug=True, port=5001)
    app.run(host='0.0.0.0',debug=True, port=4001)