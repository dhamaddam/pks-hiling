
import csv
import os
from flask import send_file
from flask import Blueprint, render_template, request, redirect, url_for, flash
dashboard_module = Blueprint('dashboard', __name__)
import pandas as pd
import pymysql
import io
from datetime import datetime
# Konfigurasi koneksi database
DB_CONFIG = {
    "host": "43.218.37.170",
    "user": "iopri",
    "password": "^c56unJ^#X",
    "database": "1011pemulliandb",
    "charset": "utf8mb4"
}


class Dashboard:
    def __init__(self):
        self.UPLOAD_FOLDER = 'uploads'
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
        self.independentVars = ['GNDVI', 'band1', 'band2', 'band3', 'NDVI', "SR"]
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.csv_file = os.path.join(self.base_dir, '..', '..', 'hasil_nsp.csv')
        
    def get_db_connection(self):
        connection = pymysql.connect(
            host='43.218.37.170',
            user='iopri',
            password='^c56unJ^#X',  # ganti dengan password MySQL kamu
            database='1011pemulliandb',  # ganti dengan nama DB kamu
            cursorclass=pymysql.cursors.DictCursor 
        )
        return connection
    def lihat_hasil_sortasi(self):
        data = []
        
        try:
            with open(self.csv_file, mode='r') as f:
                reader = csv.reader(f)
                headers = next(reader)  # Baris pertama sebagai header
                for row in reader:
                    data.append(row)
        except FileNotFoundError:
            headers = []
            data = []
        return render_template('lihat_hasil_sortasi.html', username="Admin", headers=headers, data=data)
    
    def master_data(self):
        headers = [
        'id','expt_num','cr_plan','crossing','female','male','female_gp_f','female_gp_m',
        'male_gp_f','male_gp_m','rep','block','plot','row','palm','design','sph','field',
        'planting_year','estate','population','position','clone','ortet','ha','palm_id'
        ]
        
        page = request.args.get('page', 1, type=int)
        per_page = 100
        offset = (page - 1) * per_page
        
        # Ambil filter dari query string (nama parameter di URL = no_percobaan)
        selected_no_percobaan = request.args.get('no_percobaan') or None

        connection = self.get_db_connection()
        try:
            with connection.cursor() as cursor:
                # Ambil daftar unique expt_num untuk dropdown
                cursor.execute("SELECT DISTINCT expt_num FROM master_data ORDER BY expt_num ASC")
                no_percobaan_list = [row['expt_num'] for row in cursor.fetchall()]

                # Hitung total rows (dengan atau tanpa filter)
                if selected_no_percobaan:
                    cursor.execute(
                        "SELECT COUNT(*) AS total FROM master_data WHERE expt_num = %s",
                        (selected_no_percobaan,)
                    )
                else:
                    cursor.execute("SELECT COUNT(*) AS total FROM master_data")
                total_rows = cursor.fetchone()['total']
                total_pages = (total_rows + per_page - 1) // per_page

                # Ambil data untuk halaman saat ini (dengan atau tanpa filter)
                if selected_no_percobaan:
                    cursor.execute(
                        """
                        SELECT * FROM master_data
                        WHERE expt_num = %s
                        ORDER BY id ASC
                        LIMIT %s OFFSET %s
                        """,
                        (selected_no_percobaan, per_page, offset)
                    )
                else:
                    cursor.execute(
                        "SELECT * FROM master_data ORDER BY id ASC LIMIT %s OFFSET %s",
                        (per_page, offset)
                    )
                data = cursor.fetchall()
        finally:
            connection.close()

        return render_template(
            'master_data.html',
            username="Admin",
            headers=headers,
            data=data,
            page=page,
            total_pages=total_pages,
            no_percobaan_list=no_percobaan_list,
            selected_no_percobaan=selected_no_percobaan
        )
        
    def analisa_tandan(self):
        headers = [
            'id','tanggal_panen','no_percobaan','no_kartu','no_analisa','no_baris','no_pokok',
            'no_sampel','no_persilangan','berat_tandan','stalk','tipe_buah','spikelet',
            'berat_contoh_buah','jumlah_buah','berat_buah_a','berat_buah_b','berat_mes_a',
            'berat_mes_b','berat_biji','berat_inti','berat_cangkang','mesokarp',
            'berat_mesokarp_segar','berat_mesokarp_kering','berat_mangkok','mangkok_mesocarp',
            'mangkok_mesocarp_kering','berat_kantong_kosong_a','berat_kantong_kosong_b',
            'berat_kantong_mes_a','berat_kantong_mes_b','berat_kantong_meso_sox_a',
            'berat_kantong_meso_sox_b','contoh_a','contoh_b','berat_serat_a','berat_serat_b',
            'berat_minyak_a','berat_minyak_b','persen_serat_meso_a','persen_serat_meso_b',
            'persen_minyak_mes_kering_a','persen_minyak_mes_kering_b',
            'persen_minyak_mes_segar_a','persen_minyak_mes_segar_b','kadar_air','persen_tandan',
            'persen_mesocarp','persen_cangkang','persen_inti_buah','persen_minyak_mes_kering',
            'persen_minyak_mes_segar','persen_minyak_tandan','persen_rendemen',
            'persen_inti_tandan','selisih','palm_id','created_at','updated_at'
        ]

        # Ambil parameter filter
        page = request.args.get('page', 1, type=int)
        per_page = 100
        offset = (page - 1) * per_page

        selected_no_percobaan = request.args.get('no_percobaan') or None
        selected_tahun = request.args.get('tahun_record') or None
        selected_bulan = request.args.get('bulan_record') or None

        connection = self.get_db_connection()
        try:
            with connection.cursor() as cursor:
                # Ambil list untuk dropdown filter
                cursor.execute("SELECT DISTINCT no_percobaan FROM analisa_tandan ORDER BY no_percobaan ASC")
                no_percobaan_list = [row['no_percobaan'] for row in cursor.fetchall()]

                cursor.execute("SELECT DISTINCT YEAR(tanggal_panen) AS tahun FROM analisa_tandan WHERE tanggal_panen IS NOT NULL ORDER BY tahun DESC")
                tahun_list = [row['tahun'] for row in cursor.fetchall() if row['tahun']]

                cursor.execute("SELECT DISTINCT MONTH(tanggal_panen) AS bulan FROM analisa_tandan WHERE tanggal_panen IS NOT NULL ORDER BY bulan ASC")
                bulan_list = [row['bulan'] for row in cursor.fetchall() if row['bulan']]

                # ======================
                # Build Dynamic Filter
                # ======================
                where_clause = []
                params = []

                if selected_no_percobaan:
                    where_clause.append("no_percobaan = %s")
                    params.append(selected_no_percobaan)
                if selected_tahun:
                    where_clause.append("YEAR(tanggal_panen) = %s")
                    params.append(selected_tahun)
                if selected_bulan:
                    where_clause.append("MONTH(tanggal_panen) = %s")
                    params.append(selected_bulan)

                where_sql = "WHERE " + " AND ".join(where_clause) if where_clause else ""

                # Hitung total
                count_sql = f"SELECT COUNT(*) AS total FROM analisa_tandan {where_sql}"
                cursor.execute(count_sql, params)
                total_rows = cursor.fetchone()['total']
                total_pages = (total_rows + per_page - 1) // per_page

                # Ambil data
                data_sql = f"SELECT * FROM analisa_tandan {where_sql} ORDER BY id ASC LIMIT %s OFFSET %s"
                cursor.execute(data_sql, (*params, per_page, offset))
                data = cursor.fetchall()
        finally:
            connection.close()

        return render_template(
            'analisa_tandan.html',
            username="Admin",
            headers=headers,
            data=data,
            page=page,
            total_pages=total_pages,
            no_percobaan_list=no_percobaan_list,
            tahun_list=tahun_list,
            bulan_list=bulan_list,
            selected_no_percobaan=selected_no_percobaan,
            selected_tahun=selected_tahun,
            selected_bulan=selected_bulan
        )

    
    
    def produksi(self):
        headers = [
            'expt_num','palm_id','tahun', 'bulan', 'cr_plan', 'crossing',
            'baris', 'pohon',
            'bn1', 'ffb1', 'bn2', 'ffb2', 'bn4', 'ffb4',
            'bn5', 'ffb5', 'bn6', 'ffb6',
            'tot_bn', 'tot_ffb', 'abw'
        ]

        # Pagination and filters
        page = request.args.get('page', 1, type=int)
        per_page = 100
        offset = (page - 1) * per_page

        selected_tahun = request.args.get('tahun_record') or None
        selected_bulan = request.args.get('bulan_record') or None
        selected_no_percobaan = request.args.get('no_percobaan') or None

        connection = self.get_db_connection()
        try:
            with connection.cursor() as cursor:
                # Ambil list untuk dropdown filter
                cursor.execute("SELECT DISTINCT tahun FROM produksi ORDER BY tahun DESC")
                tahun_list = [row['tahun'] for row in cursor.fetchall()]

                cursor.execute("SELECT DISTINCT bulan FROM produksi ORDER BY bulan ASC")
                bulan_list = [row['bulan'] for row in cursor.fetchall()]

                cursor.execute("SELECT DISTINCT expt_num FROM produksi ORDER BY no_percobaan ASC")
                no_percobaan_list = [row['expt_num'] for row in cursor.fetchall()]

                # Dynamic filter
                where_clause = []
                params = []

                if selected_tahun:
                    where_clause.append("tahun = %s")
                    params.append(selected_tahun)
                if selected_bulan:
                    where_clause.append("bulan = %s")
                    params.append(selected_bulan)
                if selected_no_percobaan:
                    where_clause.append("expt_num = %s")
                    params.append(selected_no_percobaan)

                where_sql = "WHERE " + " AND ".join(where_clause) if where_clause else ""

                # Total count
                count_sql = f"SELECT COUNT(*) AS total FROM produksi {where_sql}"
                cursor.execute(count_sql, params)
                total_rows = cursor.fetchone()['total']
                total_pages = (total_rows + per_page - 1) // per_page

                # Ambil data
                sql = f"""
                    SELECT * FROM produksi
                    {where_sql}
                    ORDER BY tahun DESC, bulan DESC, id ASC
                    LIMIT %s OFFSET %s
                """
                cursor.execute(sql, (*params, per_page, offset))
                data = cursor.fetchall()

        finally:
            connection.close()

        return render_template(
            'produksi.html',
            username="Admin",
            headers=headers,
            data=data,
            page=page,
            total_pages=total_pages,
            tahun_list=tahun_list,
            bulan_list=bulan_list,
            no_percobaan_list=no_percobaan_list,
            selected_tahun=selected_tahun,
            selected_bulan=selected_bulan,
            selected_no_percobaan=selected_no_percobaan
        )
    
    def vegetatif_tanaman(self):
        headers = [
            'tahun', 'bulan', 'usia_tanam', 'expt_num', 'crossing',
            'baris', 'pohon', 'palm_id',
            'tinggi_tanaman', 'lb', 'jlh_daun_frond', 'panjang_rachis', 'petiola_l', 'petiola_t',
            'p1', 'l1', 'p2', 'l2', 'p3', 'l3', 'p4', 'l4', 'p5', 'l5', 'p6', 'l6', 'hi',
            'avg_p', 'avg_l', 'la', 'tot_la', 'lai', 'pcs'
        ]

        # Pagination setup
        page = request.args.get('page', 1, type=int)
        per_page = 100
        offset = (page - 1) * per_page

        # Filter setup
        selected_tahun = request.args.get('tahun_record') or None
        selected_bulan = request.args.get('bulan_record') or None

        connection = self.get_db_connection()
        try:
            with connection.cursor() as cursor:
                # Dropdown Tahun & Bulan
                cursor.execute("SELECT DISTINCT tahun FROM vegetatif ORDER BY tahun DESC")
                tahun_list = [row['tahun'] for row in cursor.fetchall() if row['tahun']]

                cursor.execute("SELECT DISTINCT bulan FROM vegetatif ORDER BY bulan ASC")
                bulan_list = [row['bulan'] for row in cursor.fetchall() if row['bulan']]

                # Dynamic filters
                where_clause = []
                params = []
                if selected_tahun:
                    where_clause.append("tahun = %s")
                    params.append(selected_tahun)
                if selected_bulan:
                    where_clause.append("bulan = %s")
                    params.append(selected_bulan)
                
                where_sql = "WHERE " + " AND ".join(where_clause) if where_clause else ""

                # Total rows
                cursor.execute(f"SELECT COUNT(*) AS total FROM vegetatif {where_sql}", params)
                total_rows = cursor.fetchone()['total']
                total_pages = (total_rows + per_page - 1) // per_page

                # Fetch data
                sql = f"""
                    SELECT * FROM vegetatif
                    {where_sql}
                    ORDER BY tahun DESC, bulan DESC, id ASC
                    LIMIT %s OFFSET %s
                """
                cursor.execute(sql, (*params, per_page, offset))
                data = cursor.fetchall()

        finally:
            connection.close()

        return render_template(
            'vegetatif_tanaman.html',
            username="Admin",
            headers=headers,
            data=data,
            page=page,
            total_pages=total_pages,
            tahun_list=tahun_list,
            bulan_list=bulan_list,
            selected_tahun=selected_tahun,
            selected_bulan=selected_bulan
        )

    
    def sensus_tanaman(self):
        headers = [
            'tgl_pengamatan', 'tahun', 'bulan', 'expt_num', 'crossing',
            'female', 'male',
            'female_gp_f', 'female_gp_m',
            'male_gp_f', 'male_gp_m',
            'baris', 'pohon',
            'sensus_tanaman', 'palm_id'
        ]

        # Pagination setup
        page = request.args.get('page', 1, type=int)
        per_page = 100
        offset = (page - 1) * per_page

        # Filters
        selected_tahun = request.args.get('tahun_record') or None
        selected_no_percobaan = request.args.get('no_percobaan') or None

        connection = self.get_db_connection()
        try:
            with connection.cursor() as cursor:
                # Dropdown lists
                cursor.execute("SELECT DISTINCT YEAR(tgl_pengamatan) AS tahun FROM sensus_tanaman WHERE tgl_pengamatan IS NOT NULL ORDER BY tahun DESC")
                tahun_list = [row['tahun'] for row in cursor.fetchall() if row['tahun']]

                cursor.execute("SELECT DISTINCT expt_num FROM sensus_tanaman ORDER BY expt_num ASC")
                no_percobaan_list = [row['expt_num'] for row in cursor.fetchall()]

                # Build WHERE
                where_clause = []
                params = []
                if selected_tahun:
                    where_clause.append("YEAR(tgl_pengamatan) = %s")
                    params.append(selected_tahun)
                if selected_no_percobaan:
                    where_clause.append("expt_num = %s")
                    params.append(selected_no_percobaan)

                where_sql = "WHERE " + " AND ".join(where_clause) if where_clause else ""

                # Count total rows
                cursor.execute(f"SELECT COUNT(*) AS total FROM sensus_tanaman {where_sql}", params)
                total_rows = cursor.fetchone()['total']
                total_pages = (total_rows + per_page - 1) // per_page

                # Query data
                sql = f"""
                    SELECT * FROM sensus_tanaman
                    {where_sql}
                    ORDER BY tgl_pengamatan DESC, id ASC
                    LIMIT %s OFFSET %s
                """
                cursor.execute(sql, (*params, per_page, offset))
                data = cursor.fetchall()

        finally:
            connection.close()

        return render_template(
            'sensus_tanaman.html',
            username="Admin",
            headers=headers,
            data=data,
            page=page,
            total_pages=total_pages,
            tahun_list=tahun_list,
            no_percobaan_list=no_percobaan_list,
            selected_tahun=selected_tahun,
            selected_no_percobaan=selected_no_percobaan
        )

    
       
    def sex_ratio(self):
        headers = [
            'tahun', 'bulan', 'expt_num', 'female', 'male',
            'baris', 'pohon', 'palm_id',  # ✅ tambahkan id pohon
            'jantan', 'betina', 'banci', 'dompet', 'pelepah', 'sex_ratio'
        ]

        page = request.args.get('page', 1, type=int)
        per_page = 100
        offset = (page - 1) * per_page

        selected_tahun = request.args.get('tahun_record') or None
        selected_bulan = request.args.get('bulan_record') or None
        selected_no_percobaan = request.args.get('no_percobaan') or None

        connection = self.get_db_connection()
        try:
            with connection.cursor() as cursor:
                # 🧾 Dropdown filter options
                cursor.execute("SELECT DISTINCT tahun FROM sex_ratio ORDER BY tahun DESC")
                tahun_list = [row['tahun'] for row in cursor.fetchall() if row['tahun']]

                cursor.execute("SELECT DISTINCT bulan FROM sex_ratio ORDER BY bulan ASC")
                bulan_list = [row['bulan'] for row in cursor.fetchall() if row['bulan']]

                cursor.execute("SELECT DISTINCT expt_num FROM sex_ratio ORDER BY expt_num ASC")
                no_percobaan_list = [row['expt_num'] for row in cursor.fetchall() if row['expt_num']]

                # 🔍 Build dynamic filter
                where_clause, params = [], []
                if selected_tahun:
                    where_clause.append("tahun = %s")
                    params.append(selected_tahun)
                if selected_bulan:
                    where_clause.append("bulan = %s")
                    params.append(selected_bulan)
                if selected_no_percobaan:
                    where_clause.append("expt_num = %s")
                    params.append(selected_no_percobaan)

                where_sql = "WHERE " + " AND ".join(where_clause) if where_clause else ""

                # 📄 Total rows & pages
                cursor.execute(f"SELECT COUNT(*) AS total FROM sex_ratio {where_sql}", params)
                total_rows = cursor.fetchone()['total']
                total_pages = (total_rows + per_page - 1) // per_page

                # 📥 Fetch paginated data
                sql = f"""
                    SELECT * FROM sex_ratio
                    {where_sql}
                    ORDER BY tahun DESC, bulan DESC, id ASC
                    LIMIT %s OFFSET %s
                """
                cursor.execute(sql, (*params, per_page, offset))
                data = cursor.fetchall()

        finally:
            connection.close()

        return render_template(
            'sex_ratio.html',
            username="Admin",
            headers=headers,
            data=data,
            page=page,
            total_pages=total_pages,
            tahun_list=tahun_list,
            bulan_list=bulan_list,
            no_percobaan_list=no_percobaan_list,
            selected_tahun=selected_tahun,
            selected_bulan=selected_bulan,
            selected_no_percobaan=selected_no_percobaan
        )



    
    def segregasi(self):
        headers = [
            'tgl_pengamatan', 'tahun', 'bulan', 'expt_num',
            'female', 'male', 'baris', 'pohon', 'palm_id', 'tipe_buah'
        ]

        # 📄 Pagination setup
        page = request.args.get('page', 1, type=int)
        per_page = 100
        offset = (page - 1) * per_page

        # 🎚️ Filters
        selected_tahun = request.args.get('tahun_record') or None
        selected_no_percobaan = request.args.get('no_percobaan') or None

        connection = self.get_db_connection()
        try:
            with connection.cursor() as cursor:
                # 🔽 Dropdown filter options
                cursor.execute("SELECT DISTINCT tahun FROM segregasi ORDER BY tahun DESC")
                tahun_list = [row['tahun'] for row in cursor.fetchall() if row['tahun']]

                cursor.execute("SELECT DISTINCT expt_num FROM segregasi ORDER BY expt_num ASC")
                no_percobaan_list = [row['expt_num'] for row in cursor.fetchall() if row['expt_num']]

                # 🔍 Build dynamic WHERE clause
                where_clause, params = [], []
                if selected_tahun:
                    where_clause.append("tahun = %s")
                    params.append(selected_tahun)
                if selected_no_percobaan:
                    where_clause.append("expt_num = %s")
                    params.append(selected_no_percobaan)

                where_sql = "WHERE " + " AND ".join(where_clause) if where_clause else ""

                # 🧮 Count total rows
                cursor.execute(f"SELECT COUNT(*) AS total FROM segregasi {where_sql}", params)
                total_rows = cursor.fetchone()['total']
                total_pages = (total_rows + per_page - 1) // per_page if total_rows > 0 else 1

                # 📥 Fetch paginated data
                sql = f"""
                    SELECT * FROM segregasi
                    {where_sql}
                    ORDER BY tahun DESC, bulan DESC, tgl_pengamatan DESC
                    LIMIT %s OFFSET %s
                """
                cursor.execute(sql, (*params, per_page, offset))
                data = cursor.fetchall()

        finally:
            connection.close()

        # 📊 Hitung rentang data yang sedang ditampilkan
        start_row = offset + 1 if total_rows > 0 else 0
        end_row = min(offset + per_page, total_rows)

        # 🖼️ Kirim ke template
        return render_template(
            'segregasi.html',
            username="Admin",
            headers=headers,
            data=data,
            page=page,
            total_pages=total_pages,
            total_rows=total_rows,
            start_row=start_row,
            end_row=end_row,
            tahun_list=tahun_list,
            no_percobaan_list=no_percobaan_list,
            selected_tahun=selected_tahun,
            selected_no_percobaan=selected_no_percobaan
        )


    
    def export_master_data_xls(self):
        selected_no_percobaan = request.args.get('no_percobaan') or None

        connection = self.get_db_connection()
        try:
            with connection.cursor() as cursor:
                if selected_no_percobaan:
                    cursor.execute(
                        "SELECT * FROM master_data WHERE expt_num = %s ORDER BY id ASC",
                        (selected_no_percobaan,)
                    )
                else:
                    cursor.execute("SELECT * FROM master_data ORDER BY id ASC")

                rows = cursor.fetchall()
        finally:
            connection.close()

        # Convert to DataFrame
        df = pd.DataFrame(rows)

        # Generate Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Master Data')
        output.seek(0)

        filename = f"master_data_{selected_no_percobaan or 'all'}.xlsx"
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    def export_analisa_tandan_xls(self):
        selected_no_percobaan = request.args.get('no_percobaan') or None
        selected_tahun = request.args.get('tahun_record') or None
        selected_bulan = request.args.get('bulan_record') or None

        connection = self.get_db_connection()
        try:
            with connection.cursor() as cursor:
                where_clause = []
                params = []

                if selected_no_percobaan:
                    where_clause.append("no_percobaan = %s")
                    params.append(selected_no_percobaan)
                if selected_tahun:
                    where_clause.append("YEAR(tanggal_panen) = %s")
                    params.append(selected_tahun)
                if selected_bulan:
                    where_clause.append("MONTH(tanggal_panen) = %s")
                    params.append(selected_bulan)

                where_sql = "WHERE " + " AND ".join(where_clause) if where_clause else ""
                sql = f"SELECT * FROM analisa_tandan {where_sql} ORDER BY id ASC"
                cursor.execute(sql, params)
                rows = cursor.fetchall()
        finally:
            connection.close()

        df = pd.DataFrame(rows)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Analisa Tandan')
        output.seek(0)

        filename = f"analisa_tandan_{selected_no_percobaan or 'all'}_{selected_tahun or 'all'}_{selected_bulan or 'all'}.xlsx"
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    def export_produksi_xls(self):
        selected_tahun = request.args.get('tahun_record') or None
        selected_bulan = request.args.get('bulan_record') or None
        selected_no_percobaan = request.args.get('no_percobaan') or None

        connection = self.get_db_connection()
        try:
            with connection.cursor() as cursor:
                where_clause = []
                params = []

                if selected_tahun:
                    where_clause.append("tahun = %s")
                    params.append(selected_tahun)
                if selected_bulan:
                    where_clause.append("bulan = %s")
                    params.append(selected_bulan)
                if selected_no_percobaan:
                    where_clause.append("no_percobaan = %s")
                    params.append(selected_no_percobaan)

                where_sql = "WHERE " + " AND ".join(where_clause) if where_clause else ""
                sql = f"SELECT * FROM produksi {where_sql} ORDER BY tahun DESC, bulan DESC, id ASC"
                cursor.execute(sql, params)
                rows = cursor.fetchall()
        finally:
            connection.close()

        df = pd.DataFrame(rows)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Produksi')
        output.seek(0)

        filename = f"produksi_{selected_tahun or 'all'}_{selected_bulan or 'all'}_{selected_no_percobaan or 'all'}.xlsx"
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )


    def sortasi_panen(self):
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
            nsp = ((72/100) * (bmt/100)) + ((96/100) * (bkm/100)) + ((100/100) * (bm/100)) + ((98/100) * (blm)/100)
            
            nsp_prime = nsp * (bn/100)
            
            nsp = round(nsp, 2) * 100 
            nsp_prime = round(nsp_prime, 2) * 100
            
            if form['action'] == 'simpan':
                # Simpan ke CSV
                data = [
                    form['perusahaan'],
                    form['kebun'],
                    form['afdelling'],
                    fpmt, bmt, fpkm, bkm, fpm, bm, fplm, blm, bn,
                    nsp, nsp_prime
                ]
                
                file_exists = os.path.isfile(self.csv_file)

                with open(self.csv_file, mode='a', newline='') as f:
                    writer = csv.writer(f)
                    if not file_exists:
                        writer.writerow([
                            "Perusahaan", "Kebun", "Afdelling", "FPmt", "BMt", "FPKM", "BKM", "FPM", "BM", "FPLM", "BLM", "BN", "NSP", "NSP'"
                        ])
                    writer.writerow(data)

            return render_template('sortasi_panen.html', nsp=nsp, nsp_prime=nsp_prime)

        return render_template('sortasi_panen.html', username="Admin")


UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@dashboard_module.route('/upload_master_data', methods=['GET'])
def upload_master_data():
    return render_template('master_data.html', username="Admin")

@dashboard_module.route('/analisa_tandan', methods=['GET'])
def analisa_tandan():
    return render_template('analisa_tandan.html', username="Admin")

@dashboard_module.route('/upload_csv', methods=['POST'])
def upload_csv():
    file = request.files.get('file')
    if not file:
        flash("Tidak ada file yang dipilih!", "danger")
        return redirect(url_for('dashboard.upload_master_data'))

    if not file.filename.endswith('.csv'):
        flash("File harus berformat .CSV!", "warning")
        return redirect(url_for('dashboard.upload_master_data'))

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        # Baca file CSV
        # df = pd.read_csv(filepath)
        df = pd.read_csv(filepath, delimiter=';')

        # Pastikan kolom sesuai dengan tabel master_data
        expected_cols = [
            'expt_num', 'cr_plan', 'crossing', 'female', 'male',
            'female_gp_f', 'female_gp_m', 'male_gp_f', 'male_gp_m',
            'rep', 'block', 'plot', 'row', 'palm', 'design', 'sph',
            'field', 'planting_year', 'estate', 'population', 'position',
            'clone', 'ortet', 'ha', 'palm_id'
        ]

        missing_cols = [c for c in expected_cols if c not in df.columns]
        if missing_cols:
            flash(f"Kolom berikut tidak ditemukan di file CSV: {missing_cols}", "danger")
            return redirect(url_for('dashboard.upload_master_data'))

        # Koneksi ke database
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        insert_query = """
            INSERT INTO master_data (
                expt_num, cr_plan, crossing, female, male,
                female_gp_f, female_gp_m, male_gp_f, male_gp_m,
                rep, block, plot, baris, pohon, design, sph, field,
                planting_year, estate, population, pos, clone,
                ortet, ha, palm_id
            )
            VALUES (
                %(expt_num)s, %(cr_plan)s, %(crossing)s, %(female)s, %(male)s,
                %(female_gp_f)s, %(female_gp_m)s, %(male_gp_f)s, %(male_gp_m)s,
                %(rep)s, %(block)s, %(plot)s, %(row)s, %(palm)s, %(design)s, %(sph)s,
                %(field)s, %(planting_year)s, %(estate)s, %(population)s, %(position)s,
                %(clone)s, %(ortet)s, %(ha)s, %(palm_id)s
            )
        """

        # Loop setiap baris dataframe
        for _, row in df.iterrows():
            data = {col: (None if pd.isna(row[col]) else row[col]) for col in expected_cols}
            cursor.execute(insert_query, data)

        conn.commit()
        flash(f"✅ Berhasil mengunggah {len(df)} baris ke tabel master_data!", "success")

    except Exception as e:
        flash(f"❌ Terjadi kesalahan: {e}", "danger")

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

    return redirect(url_for('dashboard.upload_master_data'))



@dashboard_module.route('/upload_csv_analisa_tandan', methods=['POST'])
def upload_csv_analisa_tandan():
    file = request.files.get('file')
    if not file:
        flash("❌ Tidak ada file yang dipilih!", "danger")
        return redirect(url_for('analisa_tandan'))

    if not file.filename.endswith('.csv'):
        flash("⚠️ File harus berformat .CSV!", "warning")
        return redirect(url_for('analisa_tandan'))
    
    

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        # Baca CSV
        df = pd.read_csv(filepath, delimiter=';')
        
        if 'tgl_panen' in df.columns:
            df['tgl_panen'] = df['tgl_panen'].apply(
                lambda x: datetime.strptime(str(x), '%d.%m.%Y').strftime('%Y-%m-%d')
                if pd.notna(x) and '.' in str(x)
                else None
            )
        # Bersihkan kolom no_analisa
        df['no_analisa'] = df['no_analisa'].astype(str).str.strip()
        df['selisih'] = (
            df['selisih']
            .astype(str)
            .str.strip()  # hapus spasi di awal/akhir
            .str.replace(r'\s*-\s*', '-', regex=True)  # ubah " - 0.13" jadi "-0.13"
            .replace({'': None, 'None': None})  # kosong jadi None
        )

        df['selisih'] = pd.to_numeric(df['selisih'], errors='coerce')
        
        # Koneksi ke database
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Ambil semua no_analisa yang sudah ada di DB
        cursor.execute("SELECT no_analisa FROM analisa_tandan")
        existing = {row[0] for row in cursor.fetchall()}  # simpan dalam set untuk lookup cepat
        
        # Filter hanya data baru yang belum ada di DB
        new_df = df[~df['no_analisa'].isin(existing)]

        # Daftar kolom sesuai dengan tabel analisa_tandan
        expected_cols = [
            'tgl_panen','no_percobaan','no_kartu','no_analisa','no_baris','no_pokok',
            'no_sampel','berat_tandan','berat_stalk','berat_buah_A','type_buah',
            'berat_spikelet','berat_contoh_buah','jlh_buah','berat_biji','berat_inti',
            'berat_mangkok','mangkok_mesocarp_kering','berat_kant_kosong_A',
            'berat_kant_kosong_B','berat_kant_mes_A','berat_kant_mes_B',
            'berat_kant_mes_soxh_A','berat_kant_mes_soxh_B','no_persilangan',
            'berat_cangkang','berat_mesocarp','mangkok_mesocarp','berat_mesocarp_segar',
            'berat_mesocarp_kering','berat_mes_A','berat_mes_B','berat_contoh_A',
            'berat_contoh_B','percent_tandan','percent_mesocarp','percent_cangkang',
            'percent_inti_buah','kadar_air','berat_serat_A','berat_serat_B',
            'berat_minyak_A','berat_minyak_B','percent_serat_meso_A','percent_serat_meso_B',
            'percent_minyak_per_mes_kering_A','percent_minyak_per_mes_kering_B',
            'percent_per_mes_segar_A','percent_per_mes_segar_B',
            'percent_minyak_mes_kering','percent_minyak_mes_segar','percent_minyak_tandan',
            'percent_rendemen','percent_inti_tandan','id_pokok','selisih'
        ]

        # Cek apakah semua kolom ada
        missing_cols = [c for c in expected_cols if c not in df.columns]
        if missing_cols:
            flash(f"⚠️ Kolom berikut tidak ditemukan di file CSV: {', '.join(missing_cols)}", "danger")
            return redirect(url_for('analisa_tandan'))

        
        #check if no_analisa have insert then not insert the rows
        if new_df.empty:
            flash("⚠️ Semua data dalam CSV sudah ada di database (tidak ada yang baru).", "warning")
        else:
            # Query insert (match dengan struktur tabel MySQL)
            insert_query = """
                INSERT INTO analisa_tandan (
                    tanggal_panen, no_percobaan, no_kartu, no_analisa, no_baris, no_pokok, no_sampel,
                    berat_tandan, stalk, berat_buah_a, tipe_buah, spikelet, berat_contoh_buah, jumlah_buah,
                    berat_biji, berat_inti, berat_mangkok, mangkok_mesocarp_kering, berat_kantong_kosong_a,
                    berat_kantong_kosong_b, berat_kantong_mes_a, berat_kantong_mes_b,
                    berat_kantong_meso_sox_a, berat_kantong_meso_sox_b, no_persilangan,
                    berat_cangkang, mesokarp, mangkok_mesocarp, berat_mesokarp_segar, berat_mesokarp_kering,
                    berat_mes_a, berat_mes_b, contoh_a, contoh_b, persen_tandan, persen_mesocarp,
                    persen_cangkang, persen_inti_buah, kadar_air, berat_serat_a, berat_serat_b,
                    berat_minyak_a, berat_minyak_b, persen_serat_meso_a, persen_serat_meso_b,
                    persen_minyak_mes_kering_a, persen_minyak_mes_kering_b,
                    persen_minyak_mes_segar_a, persen_minyak_mes_segar_b,
                    persen_minyak_mes_kering, persen_minyak_mes_segar, persen_minyak_tandan,
                    persen_rendemen, persen_inti_tandan, palm_id, selisih
                )
                VALUES (
                    %(tgl_panen)s, %(no_percobaan)s, %(no_kartu)s, %(no_analisa)s, %(no_baris)s, %(no_pokok)s,
                    %(no_sampel)s, %(berat_tandan)s, %(berat_stalk)s, %(berat_buah_A)s, %(type_buah)s,
                    %(berat_spikelet)s, %(berat_contoh_buah)s, %(jlh_buah)s, %(berat_biji)s, %(berat_inti)s,
                    %(berat_mangkok)s, %(mangkok_mesocarp_kering)s, %(berat_kant_kosong_A)s,
                    %(berat_kant_kosong_B)s, %(berat_kant_mes_A)s, %(berat_kant_mes_B)s,
                    %(berat_kant_mes_soxh_A)s, %(berat_kant_mes_soxh_B)s, %(no_persilangan)s,
                    %(berat_cangkang)s, %(berat_mesocarp)s, %(mangkok_mesocarp)s,
                    %(berat_mesocarp_segar)s, %(berat_mesocarp_kering)s, %(berat_mes_A)s, %(berat_mes_B)s,
                    %(berat_contoh_A)s, %(berat_contoh_B)s, %(percent_tandan)s, %(percent_mesocarp)s,
                    %(percent_cangkang)s, %(percent_inti_buah)s, %(kadar_air)s, %(berat_serat_A)s,
                    %(berat_serat_B)s, %(berat_minyak_A)s, %(berat_minyak_B)s, %(percent_serat_meso_A)s,
                    %(percent_serat_meso_B)s, %(percent_minyak_per_mes_kering_A)s,
                    %(percent_minyak_per_mes_kering_B)s, %(percent_per_mes_segar_A)s,
                    %(percent_per_mes_segar_B)s, %(percent_minyak_mes_kering)s,
                    %(percent_minyak_mes_segar)s, %(percent_minyak_tandan)s, %(percent_rendemen)s,
                    %(percent_inti_tandan)s, %(id_pokok)s, %(selisih)s
                );
                """

            # Masukkan baris ke DB
            for _, row in df.iterrows():
                row_data = {col: (None if pd.isna(row[col]) else row[col]) for col in expected_cols}
                cursor.execute(insert_query, row_data)

            conn.commit()
            flash(f"✅ Berhasil mengunggah {len(df)} baris ke tabel analisa_tandan!", "success")

    except Exception as e:
        flash(f"❌ Terjadi kesalahan: {str(e)}", "danger")

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

    return redirect(url_for('analisa_tandan'))

@dashboard_module.route('/upload_csv_produksi', methods=['POST'])
def upload_csv_produksi():
    file = request.files.get('file')
    if not file:
        flash("❌ Tidak ada file yang dipilih!", "danger")
        return redirect(url_for('produksi'))

    if not file.filename.endswith('.csv'):
        flash("⚠️ File harus berformat .CSV!", "warning")
        return redirect(url_for('produksi'))

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        # 🧾 Baca CSV
        df = pd.read_csv(filepath, delimiter=',')

        # Normalisasi kolom
        df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]

        # Kolom wajib (sesuai CSV)
        expected_cols = [
            'tahun_bulan','female','male','id_pokok',
            'expt_num','tahun', 'bulan', 'cr_plan', 'crossing',
            'row', 'palm',
            'bn1', 'ffb1', 'bn2', 'ffb2', 'bn4', 'ffb4',
            'bn5', 'ffb5', 'bn6', 'ffb6',
            'tot_bn', 'tot_ffb', 'abw'
        ]

        # Cek kolom yang hilang
        missing = [c for c in expected_cols if c not in df.columns]
        if missing:
            flash(f"⚠️ Kolom berikut tidak ditemukan di file CSV: {', '.join(missing)}", "danger")
            return redirect(url_for('produksi'))

        # Filter data valid
        df = df[expected_cols].dropna(subset=['tahun', 'bulan', 'row', 'palm'])
        df = df.fillna(0)

        # Konversi numerik aman
        numeric_cols = [
            'bn1', 'ffb1', 'bn2', 'ffb2', 'bn4', 'ffb4',
            'bn5', 'ffb5', 'bn6', 'ffb6',
            'tot_bn', 'tot_ffb', 'abw'
        ]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # 🧮 Hitung otomatis ABW jika kosong
        df['abw'] = df.apply(
            lambda r: round((r['tot_ffb'] / r['tot_bn']), 2)
            if r['tot_bn'] not in [0, None] else 0,
            axis=1
        )

        # 🔗 Koneksi DB
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Ambil existing data
        cursor.execute("SELECT tahun, bulan, baris, pohon FROM produksi")
        existing = {(r[0], r[1], r[2], r[3]) for r in cursor.fetchall()}

        # Konversi nama kolom agar cocok dengan tabel DB (row→baris, palm→pohon)
        df.rename(columns={'row': 'baris', 'palm': 'pohon'}, inplace=True)

        # Filter data baru
        new_rows = []
        for _, row in df.iterrows():
            key = (str(row['tahun']), str(row['bulan']), str(row['baris']), str(row['pohon']))
            if key not in existing:
                new_rows.append(row)

        if not new_rows:
            flash("⚠️ Semua data sudah ada di database. Tidak ada baris baru yang dimasukkan.", "warning")
            return redirect(url_for('produksi'))

        # 📝 Query insert sesuai kolom tabel MySQL
        insert_query = """
            INSERT INTO produksi (
                tahun_bulan,female,male,palm_id,
                expt_num, tahun, bulan, cr_plan, crossing,
                baris, pohon,
                bn1, ffb1, bn2, ffb2, bn4, ffb4,
                bn5, ffb5, bn6, ffb6,
                tot_bn, tot_ffb, abw, created_at, updated_at
            ) VALUES (
                %(tahun_bulan)s,%(female)s,%(male)s,%(id_pokok)s,
                %(expt_num)s,%(tahun)s, %(bulan)s, %(cr_plan)s, %(crossing)s,
                %(baris)s, %(pohon)s,
                %(bn1)s, %(ffb1)s, %(bn2)s, %(ffb2)s, %(bn4)s, %(ffb4)s,
                %(bn5)s, %(ffb5)s, %(bn6)s, %(ffb6)s,
                %(tot_bn)s, %(tot_ffb)s, %(abw)s, NOW(), NOW()
            )
        """

        count_inserted = 0
        for _, r in df.iterrows():
            key = (str(r['tahun']), str(r['bulan']), str(r['baris']), str(r['pohon']))
            if key not in existing:
                cursor.execute(insert_query, r.to_dict())
                count_inserted += 1

        conn.commit()
        flash(f"✅ Berhasil menambahkan {count_inserted} baris baru ke tabel produksi! (ABW dihitung otomatis bila kosong)", "success")

    except Exception as e:
        try:
            conn.rollback()
        except:
            pass
        flash(f"❌ Terjadi kesalahan saat upload: {str(e)}", "danger")

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

    return redirect(url_for('produksi'))




@dashboard_module.route('/upload_csv_vegetatif', methods=['POST'])
def upload_csv_vegetatif():
    file = request.files.get('file')
    if not file:
        flash("❌ Tidak ada file yang dipilih!", "danger")
        return redirect(url_for('vegetatif_tanaman'))

    if not file.filename.endswith('.csv'):
        flash("⚠️ File harus berformat .CSV!", "warning")
        return redirect(url_for('vegetatif_tanaman'))

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        # 🧾 Baca CSV (pakai delimiter koma sesuai format Anda)
        df = pd.read_csv(filepath, delimiter=',')
        df.columns = [c.strip().lower() for c in df.columns]  # normalisasi nama kolom

        # 💡 Mapping nama kolom CSV → kolom tabel MySQL
        column_map = {
            'no_percobaan': 'expt_num',
            'no_baris': 'baris',
            'no_pokok': 'pohon',
            'id_pokok': 'palm_id',
            'lb': 'lb',
            'petiola_l': 'petiola_l',
            'petiola_t': 'petiola_t',
            'n': 'n',
            'p1': 'p1', 'l1': 'l1',
            'p2': 'p2', 'l2': 'l2',
            'p3': 'p3', 'l3': 'l3',
            'p4': 'p4', 'l4': 'l4',
            'p5': 'p5', 'l5': 'l5',
            'p6': 'p6', 'l6': 'l6',
            'hi': 'hi',
            'avg_p': 'avg_p',
            'avg_l': 'avg_l',
            'la': 'la',
            'tot_la': 'tot_la',
            'lai': 'lai',
            'pcs': 'pcs',
            'tahun': 'tahun',
            'bulan': 'bulan',
            'usia_tanam': 'usia_tanam'
        }
        df.rename(columns=column_map, inplace=True)

        # ✅ Urutan kolom sesuai tabel vegetatif MySQL
        expected_cols = [
            'expt_num', 'crossing', 'female', 'male',
            'baris', 'pohon', 'tinggi_tanaman', 'lb',
            'jlh_daun_frond', 'panjang_rachis',
            'petiola_l', 'petiola_t', 'n',
            'p1','l1','p2','l2','p3','l3','p4','l4','p5','l5','p6','l6','hi',
            'avg_p','avg_l','la','tot_la','lai','pcs',
            'palm_id','tahun','bulan','usia_tanam'
        ]

        # 🚨 Cek kolom hilang
        missing = [c for c in expected_cols if c not in df.columns]
        if missing:
            flash(f"⚠️ Kolom berikut tidak ditemukan di file CSV: {', '.join(missing)}", "danger")
            return redirect(url_for('vegetatif_tanaman'))

        # ✨ Bersihkan data
        df = df[expected_cols].fillna(0)

        # Pastikan tipe numerik aman
        numeric_cols = [
            'tinggi_tanaman','lb','jlh_daun_frond','panjang_rachis','petiola_l','petiola_t','n',
            'p1','l1','p2','l2','p3','l3','p4','l4','p5','l5','p6','l6',
            'hi','avg_p','avg_l','la','tot_la','lai','usia_tanam'
        ]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # 🔗 Koneksi DB
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 🔍 Cek duplikat: kombinasi (expt_num, tahun, bulan, baris, pohon)
        cursor.execute("SELECT expt_num, tahun, bulan, baris, pohon FROM vegetatif")
        existing = {(str(r[0]), str(r[1]), str(r[2]), str(r[3]), str(r[4])) for r in cursor.fetchall()}

        # 🆕 Filter data baru
        new_rows = []
        for _, row in df.iterrows():
            key = (str(row['expt_num']), str(row['tahun']), str(row['bulan']), str(row['baris']), str(row['pohon']))
            if key not in existing:
                new_rows.append(tuple(row[c] for c in expected_cols))

        if not new_rows:
            flash("⚠️ Semua data sudah ada di database. Tidak ada baris baru yang dimasukkan.", "warning")
            return redirect(url_for('vegetatif_tanaman'))

        # 📝 Query Insert
        insert_query = f"""
            INSERT INTO vegetatif ({', '.join(expected_cols)})
            VALUES ({', '.join(['%s'] * len(expected_cols))})
        """
        cursor.executemany(insert_query, new_rows)
        conn.commit()

        flash(f"✅ Berhasil mengunggah {len(new_rows)} baris data vegetatif baru!", "success")

    except Exception as e:
        try:
            conn.rollback()
        except:
            pass
        flash(f"❌ Terjadi kesalahan saat upload: {str(e)}", "danger")

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

    return redirect(url_for('vegetatif_tanaman'))



@dashboard_module.route('/export_vegetatif_xls')
def export_vegetatif_xls():
    tahun = request.args.get('tahun_record')
    bulan = request.args.get('bulan_record')

    conn = pymysql.connect(**DB_CONFIG)
    query = "SELECT * FROM vegetatif WHERE 1=1"
    params = []
    if tahun:
        query += " AND tahun=%s"; params.append(tahun)
    if bulan:
        query += " AND bulan=%s"; params.append(bulan)

    df = pd.read_sql(query, conn, params=params)
    conn.close()

    if df.empty:
        flash("⚠️ Tidak ada data untuk diekspor.", "warning")
        return redirect(url_for('vegetatif'))

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Vegetatif')
    output.seek(0)

    return send_file(output,
                     as_attachment=True,
                     download_name=f"Data_Vegetatif_{tahun or 'All'}_{bulan or 'All'}.xlsx",
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@dashboard_module.route('/upload_csv_sensus', methods=['POST'])
def upload_csv_sensus():
    file = request.files.get('file')
    if not file:
        flash("❌ Tidak ada file yang dipilih!", "danger")
        return redirect(url_for('sensus_tanaman'))

    if not file.filename.endswith('.csv'):
        flash("⚠️ File harus berformat .CSV!", "warning")
        return redirect(url_for('sensus_tanaman'))

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        # 🧾 Baca CSV
        df = pd.read_csv(filepath, delimiter=',')
        df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]

        # 🧭 Peta nama kolom CSV → tabel MySQL
        column_map = {
            'no_percobaan': 'expt_num',
            'no_baris': 'baris',
            'no_pokok': 'pohon',
            'id_pokok': 'palm_id'
        }
        df.rename(columns=column_map, inplace=True)

        expected_cols = [
            'tgl_pengamatan', 'tahun', 'bulan', 'expt_num', 'crossing',
            'female', 'male', 'female_gp_f', 'female_gp_m',
            'male_gp_f', 'male_gp_m', 'baris', 'pohon',
            'sensus_tanaman', 'palm_id'
        ]

        # 🚨 Cek kolom yang hilang
        missing = [c for c in expected_cols if c not in df.columns]
        if missing:
            flash(f"⚠️ Kolom berikut tidak ditemukan di file CSV: {', '.join(missing)}", "danger")
            return redirect(url_for('sensus_tanaman'))

        # 🧹 Bersihkan data kosong
        df = df[expected_cols].fillna('')

        # 📅 Konversi format tanggal
        df['tgl_pengamatan'] = pd.to_datetime(df['tgl_pengamatan'], errors='coerce')

        # 🗓️ Jika kolom tahun/bulan kosong, isi otomatis dari tgl_pengamatan
        df['tahun'] = df['tahun'].replace('', None)
        df['bulan'] = df['bulan'].replace('', None)
        df['tahun'] = df.apply(
            lambda r: r['tgl_pengamatan'].year if pd.isna(r['tahun']) and pd.notna(r['tgl_pengamatan']) else r['tahun'],
            axis=1
        )
        df['bulan'] = df.apply(
            lambda r: r['tgl_pengamatan'].month if pd.isna(r['bulan']) and pd.notna(r['tgl_pengamatan']) else r['bulan'],
            axis=1
        )

        # 🔗 Koneksi database
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 🧩 Ambil data existing untuk hindari duplikat
        cursor.execute("SELECT expt_num, palm_id, tgl_pengamatan FROM sensus_tanaman")
        existing = {(str(r[0]), str(r[1]), str(r[2])) for r in cursor.fetchall()}

        # 🆕 Filter data baru
        new_rows = []
        for _, r in df.iterrows():
            key = (str(r['expt_num']), str(r['palm_id']), str(r['tgl_pengamatan'].date() if pd.notna(r['tgl_pengamatan']) else ''))
            if key not in existing:
                new_rows.append(tuple(r[c] for c in expected_cols))

        if not new_rows:
            flash("⚠️ Semua data sudah ada di database. Tidak ada baris baru yang dimasukkan.", "warning")
            return redirect(url_for('sensus_tanaman'))

        # 📝 Query insert sesuai struktur tabel
        insert_query = f"""
            INSERT INTO sensus_tanaman (
                tgl_pengamatan, tahun, bulan, expt_num, crossing,
                female, male, female_gp_f, female_gp_m,
                male_gp_f, male_gp_m, baris, pohon,
                sensus_tanaman, palm_id
            ) VALUES (
                {', '.join(['%s'] * len(expected_cols))}
            )
        """

        cursor.executemany(insert_query, new_rows)
        conn.commit()

        flash(f"✅ Berhasil menambahkan {len(new_rows)} baris baru ke tabel sensus_tanaman!", "success")

    except Exception as e:
        try:
            conn.rollback()
        except:
            pass
        flash(f"❌ Terjadi kesalahan saat upload: {str(e)}", "danger")

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

    return redirect(url_for('sensus_tanaman'))


@dashboard_module.route('/export_sensus_xls')
def export_sensus_xls():
    selected_tahun = request.args.get('tahun_record') or None
    selected_no_percobaan = request.args.get('no_percobaan') or None

    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor() as cursor:
            where_clause = []
            params = []
            if selected_tahun:
                where_clause.append("YEAR(tgl_pengamatan) = %s")
                params.append(selected_tahun)
            if selected_no_percobaan:
                where_clause.append("expt_num = %s")
                params.append(selected_no_percobaan)
            where_sql = "WHERE " + " AND ".join(where_clause) if where_clause else ""

            sql = f"SELECT * FROM sensus_tanaman {where_sql} ORDER BY tgl_pengamatan DESC"
            cursor.execute(sql, params)
            rows = cursor.fetchall()
    finally:
        connection.close()

    df = pd.DataFrame(rows)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sensus Tanaman')
    output.seek(0)

    filename = f"sensus_tanaman_{selected_tahun or 'all'}_{selected_no_percobaan or 'all'}.xlsx"
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@dashboard_module.route('/upload_csv_sex_ratio', methods=['POST'])
def upload_csv_sex_ratio():
    file = request.files.get('file')
    if not file:
        flash("❌ Tidak ada file yang dipilih!", "danger")
        return redirect(url_for('sex_ratio'))

    if not file.filename.endswith('.csv'):
        flash("⚠️ File harus berformat .CSV!", "warning")
        return redirect(url_for('sex_ratio'))

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    conn = None
    cursor = None

    try:
        # 🧾 Baca CSV
        df = pd.read_csv(filepath, delimiter=',')
        df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]

        # 💡 Peta kolom CSV → tabel MySQL
        column_map = {
            'no_percobaan': 'expt_num',
            'no_baris': 'baris',
            'no_pohon': 'pohon',
            'percent_sexratio': 'sex_ratio',
            'id_pohon': 'palm_id'
        }
        df.rename(columns=column_map, inplace=True)

        # ✅ Kolom yang diharapkan di tabel SQL
        expected_cols = [
            'tahun', 'bulan', 'expt_num', 'female', 'male',
            'baris', 'pohon', 'jantan', 'betina', 'banci',
            'dompet', 'pelepah', 'sex_ratio', 'palm_id'
        ]

        # 🚨 Cek kolom hilang
        missing = [c for c in expected_cols if c not in df.columns]
        if missing:
            flash(f"⚠️ Kolom berikut tidak ditemukan di CSV: {', '.join(missing)}", "danger")
            return redirect(url_for('sex_ratio'))

        # ✨ Bersihkan data
        df = df[expected_cols].fillna(0)

        # 🔢 Konversi tipe numerik aman
        numeric_cols = ['jantan', 'betina', 'banci', 'dompet', 'pelepah', 'sex_ratio']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # 🔗 Koneksi database
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 🧩 Query insert
        insert_query = f"""
            INSERT INTO sex_ratio ({', '.join(expected_cols)})
            VALUES ({', '.join(['%s'] * len(expected_cols))})
        """

        cursor.executemany(insert_query, df.values.tolist())
        conn.commit()

        flash(f"✅ Berhasil mengunggah {len(df)} baris data Sex Ratio!", "success")

    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"❌ Terjadi kesalahan saat upload: {str(e)}", "danger")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('sex_ratio'))




@dashboard_module.route('/export_sex_ratio_xls', methods=['GET'])
def export_sex_ratio_xls(self):
    selected_tahun = request.args.get('tahun_record') or None
    selected_bulan = request.args.get('bulan_record') or None
    selected_no_percobaan = request.args.get('no_percobaan') or None

    conn = self.get_db_connection()
    try:
        with conn.cursor() as cursor:
            where_clause = []
            params = []
            if selected_tahun:
                where_clause.append("tahun = %s")
                params.append(selected_tahun)
            if selected_bulan:
                where_clause.append("bulan = %s")
                params.append(selected_bulan)
            if selected_no_percobaan:
                where_clause.append("expt_num = %s")
                params.append(selected_no_percobaan)

            where_sql = "WHERE " + " AND ".join(where_clause) if where_clause else ""
            sql = f"SELECT * FROM sex_ratio {where_sql} ORDER BY tahun DESC, bulan DESC"
            cursor.execute(sql, params)
            rows = cursor.fetchall()
    finally:
        conn.close()

    df = pd.DataFrame(rows)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sex Ratio')
    output.seek(0)

    filename = f"sex_ratio_{selected_tahun or 'all'}_{selected_bulan or 'all'}_{selected_no_percobaan or 'all'}.xlsx"
    return send_file(output, as_attachment=True, download_name=filename,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@dashboard_module.route('/upload_csv_segregasi', methods=['POST'])
def upload_csv_segregasi():
    file = request.files.get('file')
    if not file:
        flash("❌ Tidak ada file yang dipilih!", "danger")
        return redirect(url_for('segregasi'))

    if not file.filename.endswith('.csv'):
        flash("⚠️ File harus berformat .CSV!", "warning")
        return redirect(url_for('segregasi'))

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    conn = None
    cursor = None

    try:
        # 🧾 Baca CSV
        df = pd.read_csv(filepath, delimiter=',')
        df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]

        # 🧭 Pemetaan nama kolom CSV → tabel MySQL
        column_map = {
            'no_percobaan': 'expt_num',
            'no_baris': 'baris',
            'no_pohon': 'pohon',
            'id_pohon': 'palm_id',
            'type_buah': 'tipe_buah'  # ✅ ubah kolom CSV ke MySQL
        }
        df.rename(columns=column_map, inplace=True)

        # 🚫 Hapus kolom 'id' dari CSV karena AUTO_INCREMENT di DB
        if 'id' in df.columns:
            df.drop(columns=['id'], inplace=True)

        # ✅ Kolom sesuai tabel MySQL
        expected_cols = [
            'tgl_pengamatan', 'tahun', 'bulan', 'expt_num',
            'female', 'male', 'baris', 'pohon', 'palm_id', 'tipe_buah'
        ]

        # 🚨 Cek kolom wajib
        missing = [c for c in expected_cols if c not in df.columns]
        if missing:
            flash(f"⚠️ Kolom berikut tidak ditemukan di file CSV: {', '.join(missing)}", "danger")
            return redirect(url_for('segregasi'))

        # ✨ Bersihkan & konversi data
        df = df[expected_cols].fillna('')
        df['tgl_pengamatan'] = pd.to_datetime(df['tgl_pengamatan'], errors='coerce').dt.date

        # 🔗 Koneksi DB
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 🧩 Query Insert
        insert_query = f"""
            INSERT INTO segregasi ({', '.join(expected_cols)})
            VALUES ({', '.join(['%s'] * len(expected_cols))})
        """
        cursor.executemany(insert_query, df.values.tolist())
        conn.commit()

        flash(f"✅ Berhasil mengunggah {len(df)} baris data Segregasi!", "success")

    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"❌ Terjadi kesalahan saat upload: {str(e)}", "danger")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('segregasi'))


@dashboard_module.route('/export_segregasi_xls')
def export_segregasi_xls():
    selected_tahun = request.args.get('tahun_record') or None
    selected_no_percobaan = request.args.get('no_percobaan') or None

    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            where_clause, params = [], []
            if selected_tahun:
                where_clause.append("tahun = %s")
                params.append(selected_tahun)
            if selected_no_percobaan:
                where_clause.append("expt_num = %s")
                params.append(selected_no_percobaan)

            where_sql = "WHERE " + " AND ".join(where_clause) if where_clause else ""
            cursor.execute(f"SELECT * FROM segregasi {where_sql} ORDER BY tahun DESC, bulan DESC, tgl_pengamatan DESC", params)
            rows = cursor.fetchall()
    finally:
        conn.close()

    df = pd.DataFrame(rows)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Segregasi')
    output.seek(0)

    filename = f"Segregasi_{selected_tahun or 'all'}_{selected_no_percobaan or 'all'}.xlsx"
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
