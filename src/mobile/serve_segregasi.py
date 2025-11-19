import os
import pymysql
from datetime import datetime
from flask import Blueprint, request, jsonify
from src.helper.Logfile import LogFile

# 🔹 Blueprint name and base URL
segregasi_module = Blueprint('segregasi_module', __name__)

class serveSegregasi:
    def __init__(self):
        self.logging = LogFile("daemon")
        self.logging.write("info", "serveSegregasi initialized")

        self.UPLOAD_FOLDER = 'uploads'
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

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
    def get_segregasi_mapping(self):
        self.logging.write("info", "get_segregasi_mapping called")
        return {
            "id": "id",
            "tgl_pengamatan": "tgl_pengamatan",
            "tahun": "tahun",
            "bulan": "bulan",
            "expt_num": "expt_num",
            "female": "female",
            "male": "male",
            "baris": "baris",
            "pohon": "pohon",
            "palm_id": "palm_id",
            "tipe_buah": "tipe_buah",
            "created_at": "created_at"
        }

    # =====================
    # JSON → DB
    # =====================
    def map_to_db(self, payload):
        self.logging.write("info", f"map_to_db called with payload: {payload}")

        mapping = self.get_segregasi_mapping()
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

        mapping = self.get_segregasi_mapping()
        reverse_map = {v: k for k, v in mapping.items()}

        result = {reverse_map[k]: v for k, v in db_row.items() if k in reverse_map}

        self.logging.write("info", f"map_to_mobile result: {result}")
        return result

    # =====================
    # INSERT
    # =====================
    def insert_segregasi(self, payload):
        self.logging.write("info", f"insert_segregasi called with: {payload}")

        data = self.map_to_db(payload)
        placeholders = ", ".join(["%s"] * len(data))
        columns = ", ".join(data.keys())
        values = tuple(data.values())

        query = f"INSERT INTO segregasi ({columns}) VALUES ({placeholders})"

        self.logging.write("info", f"Executing SQL: {query}")
        self.logging.write("info", f"Values: {values}")

        try:
            conn = pymysql.connect(**self.db_config)
            with conn.cursor() as cursor:
                cursor.execute(query, values)
                conn.commit()
            conn.close()

            self.logging.write("info", "Insert segregasi success")
            return {"status": "success", "message": "Segregasi data inserted successfully"}

        except Exception as e:
            self.logging.write("error", f"Insert error: {str(e)}")
            return {"status": "error", "message": str(e)}

    # =====================
    # GET
    # =====================
    def get_segregasi(self, id=None):
        self.logging.write("info", f"get_segregasi called, id={id}")

        try:
            conn = pymysql.connect(**self.db_config)
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            if id:
                query = "SELECT * FROM segregasi WHERE id=%s"
                self.logging.write("info", f"Executing SQL: {query} | id={id}")
                cursor.execute(query, (id,))
            else:
                query = "SELECT * FROM segregasi ORDER BY created_at DESC"
                self.logging.write("info", f"Executing SQL: {query}")
                cursor.execute(query)

            result = cursor.fetchall()
            conn.close()

            mapped = [self.map_to_mobile(row) for row in result]
            self.logging.write("info", f"get_segregasi result count: {len(mapped)}")

            return mapped

        except Exception as e:
            self.logging.write("error", f"Get error: {str(e)}")
            return {"status": "error", "message": str(e)}


# ==========================================================
# ROUTES
# ==========================================================

segregasi_service = serveSegregasi()

@segregasi_module.route('/api/insert', methods=['POST', 'GET'])
def api_insert_segregasi():
    try:
        segregasi_service.logging.write("info", "api_insert_segregasi hit")

        if request.method == 'POST':
            if not request.is_json:
                segregasi_service.logging.write("error", "Invalid Content-Type")
                return jsonify({"status": "error", "message": "Content-Type must be application/json"}), 415

            payload = request.get_json()
            segregasi_service.logging.write("info", f"POST payload: {payload}")

            result = segregasi_service.insert_segregasi(payload)
            return jsonify(result)

        elif request.method == 'GET':
            id = request.args.get('id')
            segregasi_service.logging.write("info", f"GET id={id}")

            data = segregasi_service.get_segregasi(id)
            return jsonify(data)

    except Exception as e:
        segregasi_service.logging.write("error", f"Route error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})
