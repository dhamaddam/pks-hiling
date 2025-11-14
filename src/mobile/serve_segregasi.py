import os
import pymysql
from datetime import datetime
from flask import Blueprint, request, jsonify

# 🔹 Blueprint name and base URL
segregasi_module = Blueprint('segregasi_module', __name__)

class serveSegregasi:
    def __init__(self):
        # Optional upload folder
        self.UPLOAD_FOLDER = 'uploads'
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        # ✅ Database connection configuration
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
    def get_segregasi_mapping(self):
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

    # 🔁 Convert JSON → DB
    def map_to_db(self, payload):
        mapping = self.get_segregasi_mapping()
        result = {}
        for key, val in payload.items():
            if key in mapping:
                result[mapping[key]] = val

        # Add timestamp automatically
        if 'created_at' not in result:
            result['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return result

    # 🔁 Convert DB → JSON for mobile response
    def map_to_mobile(self, db_row):
        mapping = self.get_segregasi_mapping()
        reverse_map = {v: k for k, v in mapping.items()}
        return {reverse_map[k]: v for k, v in db_row.items() if k in reverse_map}

    # =====================
    # 💾 INSERT DATA
    # =====================
    def insert_segregasi(self, payload):
        data = self.map_to_db(payload)
        placeholders = ", ".join(["%s"] * len(data))
        columns = ", ".join(data.keys())
        values = tuple(data.values())

        query = f"INSERT INTO segregasi ({columns}) VALUES ({placeholders})"

        try:
            conn = pymysql.connect(**self.db_config)
            with conn.cursor() as cursor:
                cursor.execute(query, values)
                conn.commit()
            conn.close()
            return {"status": "success", "message": "Segregasi data inserted successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # =====================
    # 📥 GET DATA
    # =====================
    def get_segregasi(self, id=None):
        conn = pymysql.connect(**self.db_config)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        try:
            if id:
                cursor.execute("SELECT * FROM segregasi WHERE id=%s", (id,))
            else:
                cursor.execute("SELECT * FROM segregasi ORDER BY created_at DESC")

            result = cursor.fetchall()
            conn.close()

            return [self.map_to_mobile(row) for row in result]
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ==========================================================
# 🔹 API ROUTES
# ==========================================================

segregasi_service = serveSegregasi()

@segregasi_module.route('/api/insert', methods=['POST', 'GET'])
def api_insert_segregasi():
    if request.method == 'POST':
        if not request.is_json:
            return jsonify({"status": "error", "message": "Content-Type must be application/json"}), 415

        payload = request.get_json()
        result = segregasi_service.insert_segregasi(payload)
        return jsonify(result)

    elif request.method == 'GET':
        id = request.args.get('id')
        data = segregasi_service.get_segregasi(id)
        return jsonify(data)
