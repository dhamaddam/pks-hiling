import os
import pymysql
from datetime import datetime
from flask import Blueprint, request, jsonify

# 🔹 Blueprint without prefix (we’ll use full route path manually)
sensus_tanaman_module = Blueprint('sensus_tanaman_module', __name__)

class serveSensusTanaman:
    def __init__(self):
        self.UPLOAD_FOLDER = 'uploads'
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        # ✅ Database connection config
        self.db_config = {
            'host': '43.218.37.170',
            'user': 'iopri',
            'password': '^c56unJ^#X',
            'database': '1011pemulliandb',
            'cursorclass': pymysql.cursors.DictCursor
        }

    # =====================
    # 🔹 MAPPING FIELDS
    # =====================
    def get_sensus_mapping(self):
        return {
            "id": "id",
            "tgl_pengamatan": "tgl_pengamatan",
            "tahun": "tahun",
            "bulan": "bulan",
            "expt_num": "expt_num",
            "crossing": "crossing",
            "female": "female",
            "male": "male",
            "female_gp_f": "female_gp_f",
            "female_gp_m": "female_gp_m",
            "male_gp_f": "male_gp_f",
            "male_gp_m": "male_gp_m",
            "baris": "baris",
            "pohon": "pohon",
            "sensus_tanaman": "sensus_tanaman",
            "palm_id": "palm_id",
            "created_at": "created_at"
        }

    # 🔁 JSON → DB
    def map_to_db(self, payload):
        mapping = self.get_sensus_mapping()
        result = {}
        for key, val in payload.items():
            if key in mapping:
                result[mapping[key]] = val
        # Add timestamp automatically
        if 'created_at' not in result:
            result['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return result

    # 🔁 DB → JSON
    def map_to_mobile(self, db_row):
        mapping = self.get_sensus_mapping()
        reverse_map = {v: k for k, v in mapping.items()}
        return {reverse_map[k]: v for k, v in db_row.items() if k in reverse_map}

    # =====================
    # 💾 INSERT
    # =====================
    def insert_sensus(self, payload):
        data = self.map_to_db(payload)
        placeholders = ", ".join(["%s"] * len(data))
        columns = ", ".join(data.keys())
        values = tuple(data.values())
        query = f"INSERT INTO sensus_tanaman ({columns}) VALUES ({placeholders})"

        try:
            conn = pymysql.connect(**self.db_config)
            with conn.cursor() as cursor:
                cursor.execute(query, values)
                conn.commit()
            conn.close()
            return {"status": "success", "message": "Sensus Tanaman data inserted successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # =====================
    # 📥 GET
    # =====================
    def get_sensus(self, id=None):
        conn = pymysql.connect(**self.db_config)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        try:
            if id:
                cursor.execute("SELECT * FROM sensus_tanaman WHERE id=%s", (id,))
            else:
                cursor.execute("SELECT * FROM sensus_tanaman ORDER BY created_at DESC")
            result = cursor.fetchall()
            conn.close()
            return [self.map_to_mobile(row) for row in result]
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ==========================================================
# 🔹 FLASK ROUTES
# ==========================================================

sensus_service = serveSensusTanaman()

@sensus_tanaman_module.route('/api/insert', methods=['POST', 'GET'])
def api_insert_sensus_tanaman():
    if request.method == 'POST':
        if not request.is_json:
            return jsonify({
                "status": "error",
                "message": "Content-Type must be application/json"
            }), 415

        payload = request.get_json()
        result = sensus_service.insert_sensus(payload)
        return jsonify(result)

    elif request.method == 'GET':
        id = request.args.get('id')
        data = sensus_service.get_sensus(id)
        return jsonify(data)
