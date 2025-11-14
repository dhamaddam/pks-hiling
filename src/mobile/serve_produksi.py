import os
import pymysql
from datetime import datetime
from flask import Blueprint, request, jsonify

# 🔹 Use a more specific Blueprint name
produksi_module = Blueprint('produksi_module', __name__)

class serveProduksi:
    def __init__(self):
        self.UPLOAD_FOLDER = 'uploads'
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.csv_file = os.path.join(self.base_dir, '..', '..', 'hasil_nsp.csv')
        # ✅ Database configuration
        self.db_config = {
            'host': '43.218.37.170',
            'user': 'iopri',
            'password': '^c56unJ^#X',
            'database': '1011pemulliandb',
            'cursorclass': pymysql.cursors.DictCursor
        }

    # =====================
    # 🔹 MAPPING DATA
    # =====================
    def get_produksi_mapping(self):
        return {
            'id': 'id',
            'noPohon': 'pohon',
            'noPersilangan': 'persilangan',
            'pohonKe': 'pohonKe',
            'bn1': 'bn1',
            'bn2': 'bn2',
            'bn3': 'bn3',
            'bn4': 'bn4',
            'bn5': 'bn5',
            'bn6': 'bn6',
            'program': 'program',
            'tanggalPengamatan': 'tanggalpengamatan',
            'ffb1': 'ffb1',
            'ffb2': 'ffb2',
            'ffb3': 'ffb3',
            'ffb4': 'ffb4',
            'ffb5': 'ffb5',
            'ffb6': 'ffb6',
            'created_at': 'created_at'
        }

    # 🔁 Convert payload Flutter -> format database
    def map_to_db(self, payload):
        mapping = self.get_produksi_mapping()
        result = {}
        for key, val in payload.items():
            if key in mapping:
                result[mapping[key]] = val
        # ✅ add timestamp automatically if not provided
        if 'created_at' not in result:
            result['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return result

    # 🔁 Convert result database -> format Flutter
    def map_to_mobile(self, db_row):
        mapping = self.get_produksi_mapping()
        reverse_map = {v: k for k, v in mapping.items()}
        return {reverse_map[k]: v for k, v in db_row.items() if k in reverse_map}

    # =====================
    # 💾 INSERT DATA
    # =====================
    def insert_produksi(self, payload):
        data = self.map_to_db(payload)
        placeholders = ", ".join(["%s"] * len(data))
        columns = ", ".join(data.keys())
        values = tuple(data.values())

        query = f"INSERT INTO produksi ({columns}) VALUES ({placeholders})"

        try:
            conn = pymysql.connect(**self.db_config)
            with conn.cursor() as cursor:
                cursor.execute(query, values)
                conn.commit()
            conn.close()
            return {"status": "success", "message": "Data inserted successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # =====================
    # 📥 GET DATA
    # =====================
    def get_produksi(self, id=None):
        conn = pymysql.connect(**self.db_config)
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        try:
            if id:
                cursor.execute("SELECT * FROM produksi WHERE id=%s", (id,))
            else:
                cursor.execute("SELECT * FROM produksi")
            
            result = cursor.fetchall()
            conn.close()

            # convert to Flutter format
            return [self.map_to_mobile(row) for row in result]
        except Exception as e:
            return {"status": "error", "message": str(e)}

# ==========================================================
# 🔹 FLASK ROUTES
# ==========================================================

produksi_service = serveProduksi()

@produksi_module.route('/api/insert', methods=['GET', 'POST'])
def api_produksi():
    if request.method == 'POST':
        payload = request.get_json()
        result = produksi_service.insert_produksi(payload)
        return jsonify(result)

    elif request.method == 'GET':
        id = request.args.get('id')
        data = produksi_service.get_produksi(id)
        return jsonify(data)
