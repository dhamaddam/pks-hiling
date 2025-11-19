import os
import pymysql
from datetime import datetime
from flask import Blueprint, request, jsonify
from src.helper.Logfile import LogFile

# 🔹 Blueprint
produksi_module = Blueprint('produksi_module', __name__)

class serveProduksi:
    def __init__(self):
        self.logging = LogFile("daemon")
        self.logging.write("info", "serveProduksi initialized")

        self.UPLOAD_FOLDER = 'uploads'
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.csv_file = os.path.join(self.base_dir, '..', '..', 'hasil_nsp.csv')

        # Database configuration
        self.db_config = {
            'host': '43.218.37.170',
            'user': 'iopri',
            'password': '^c56unJ^#X',
            'database': '1011pemulliandb',
            'cursorclass': pymysql.cursors.DictCursor
        }

    # =====================
    # FIELD MAPPING
    # =====================
    def get_produksi_mapping(self):
        self.logging.write("info", "get_produksi_mapping called")
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

    # =====================
    # JSON → DB
    # =====================
    def map_to_db(self, payload):
        self.logging.write("info", f"map_to_db called with payload: {payload}")

        mapping = self.get_produksi_mapping()
        result = {}
        for key, val in payload.items():
            if key in mapping:
                result[mapping[key]] = val

        if 'created_at' not in result:
            result['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.logging.write("info", f"map_to_db result: {result}")
        return result

    # =====================
    # DB → JSON
    # =====================
    def map_to_mobile(self, db_row):
        self.logging.write("info", f"map_to_mobile called with row: {db_row}")

        mapping = self.get_produksi_mapping()
        reverse_map = {v: k for k, v in mapping.items()}
        result = {reverse_map[k]: v for k, v in db_row.items() if k in reverse_map}

        self.logging.write("info", f"map_to_mobile result: {result}")
        return result

    # =====================
    # INSERT
    # =====================
    def insert_produksi(self, payload):
        self.logging.write("info", f"insert_produksi called with: {payload}")

        data = self.map_to_db(payload)
        placeholders = ", ".join(["%s"] * len(data))
        columns = ", ".join(data.keys())
        values = tuple(data.values())

        query = f"INSERT INTO produksi ({columns}) VALUES ({placeholders})"

        self.logging.write("info", f"Executing SQL: {query}")
        self.logging.write("info", f"Values: {values}")

        try:
            conn = pymysql.connect(**self.db_config)
            with conn.cursor() as cursor:
                cursor.execute(query, values)
                conn.commit()
            conn.close()

            self.logging.write("info", "Insert produksi success")
            return {"status": "success", "message": "Data inserted successfully"}

        except Exception as e:
            self.logging.write("error", f"Insert error: {str(e)}")
            return {"status": "error", "message": str(e)}

    # =====================
    # GET
    # =====================
    def get_produksi(self, id=None):
        self.logging.write("info", f"get_produksi called, id={id}")

        try:
            conn = pymysql.connect(**self.db_config)
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            if id:
                query = "SELECT * FROM produksi WHERE id=%s"
                self.logging.write("info", f"Executing SQL: {query} | id={id}")
                cursor.execute(query, (id,))
            else:
                query = "SELECT * FROM produksi"
                self.logging.write("info", f"Executing SQL: {query}")
                cursor.execute(query)

            result = cursor.fetchall()
            conn.close()

            mapped = [self.map_to_mobile(row) for row in result]
            self.logging.write("info", f"get_produksi result count: {len(mapped)}")

            return mapped

        except Exception as e:
            self.logging.write("error", f"Get error: {str(e)}")
            return {"status": "error", "message": str(e)}


# ==========================================================
# ROUTES
# ==========================================================

produksi_service = serveProduksi()

@produksi_module.route('/api/insert', methods=['GET', 'POST'])
def api_produksi():
    try:
        produksi_service.logging.write("info", "api_produksi hit")

        if request.method == 'POST':
            payload = request.get_json()
            produksi_service.logging.write("info", f"POST payload: {payload}")

            result = produksi_service.insert_produksi(payload)
            return jsonify(result)

        elif request.method == 'GET':
            id = request.args.get('id')
            produksi_service.logging.write("info", f"GET id={id}")

            data = produksi_service.get_produksi(id)
            return jsonify(data)

    except Exception as e:
        produksi_service.logging.write("error", f"Route error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})
