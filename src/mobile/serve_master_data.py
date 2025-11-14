import os
import pymysql
from datetime import datetime
from flask import Blueprint, request, jsonify

# 🔹 Blueprint without prefix (manual route)
master_data_module = Blueprint('master_data_module', __name__)

class serveMasterData:
    def __init__(self):
        self.UPLOAD_FOLDER = 'uploads'
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        # ✅ Database configuration
        self.db_config = {
            'host': '43.218.37.170',
            'user': 'iopri',
            'password': '^c56unJ^#X',
            'database': '1011pemulliandb',
            'cursorclass': pymysql.cursors.DictCursor
        }

    # =====================
    # 🔹 FIELD MAPPING
    # =====================
    def get_master_mapping(self):
        return {
            "id": "id",
            "expt_num": "expt_num",
            "cr_plan": "cr_plan",
            "crossing": "crossing",
            "female": "female",
            "male": "male",
            "female_gp_f": "female_gp_f",
            "female_gp_m": "female_gp_m",
            "male_gp_f": "male_gp_f",
            "male_gp_m": "male_gp_m",
            "rep": "rep",
            "block": "block",
            "plot": "plot",
            "baris": "baris",
            "pohon": "pohon",
            "design": "design",
            "sph": "sph",
            "field": "field",
            "planting_year": "planting_year",
            "estate": "estate",
            "population": "population",
            "pos": "pos",
            "clone": "clone",
            "ortet": "ortet",
            "ha": "ha",
            "palm_id": "palm_id",
            "created_at": "created_at"
        }

    # 🔁 Convert JSON → DB
    def map_to_db(self, payload):
        mapping = self.get_master_mapping()
        result = {}
        for key, val in payload.items():
            if key in mapping:
                result[mapping[key]] = val
        # Auto timestamp
        if 'created_at' not in result:
            result['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return result

    # 🔁 Convert DB → JSON for response
    def map_to_mobile(self, db_row):
        mapping = self.get_master_mapping()
        reverse_map = {v: k for k, v in mapping.items()}
        return {reverse_map[k]: v for k, v in db_row.items() if k in reverse_map}

    # =====================
    # 💾 INSERT DATA
    # =====================
    def insert_master_data(self, payload):
        data = self.map_to_db(payload)
        placeholders = ", ".join(["%s"] * len(data))
        columns = ", ".join(data.keys())
        values = tuple(data.values())
        query = f"INSERT INTO master_data ({columns}) VALUES ({placeholders})"

        try:
            conn = pymysql.connect(**self.db_config)
            with conn.cursor() as cursor:
                cursor.execute(query, values)
                conn.commit()
            conn.close()
            return {"status": "success", "message": "Master Data inserted successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # =====================
    # 📥 GET DATA
    # =====================
    def get_master_data(self, id=None):
        conn = pymysql.connect(**self.db_config)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        try:
            if id:
                cursor.execute("SELECT * FROM master_data WHERE id=%s", (id,))
            else:
                cursor.execute("SELECT * FROM master_data ORDER BY created_at DESC")
            result = cursor.fetchall()
            conn.close()
            return [self.map_to_mobile(row) for row in result]
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ==========================================================
# 🔹 FLASK ROUTES
# ==========================================================

master_service = serveMasterData()

@master_data_module.route('/api/insert', methods=['POST', 'GET'])
def api_insert_master_data():
    if request.method == 'POST':
        if not request.is_json:
            return jsonify({
                "status": "error",
                "message": "Content-Type must be application/json"
            }), 415

        payload = request.get_json()
        result = master_service.insert_master_data(payload)
        return jsonify(result)

    elif request.method == 'GET':
        id = request.args.get('id')
        data = master_service.get_master_data(id)
        return jsonify(data)
